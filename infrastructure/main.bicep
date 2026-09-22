param location string = 'northeurope'
param appServiceLocation string = 'westeurope'
param jenkinsPrincipalId string

param foundryResourceName string = 'foundry-armen-sweden-2026'
param appServicePlanName string = 'plan-azure-learning'
param webAppName string = 'armen-storage-demo-2026'
param pythonVersion string = '3.14'
param storageAccountName string = 'starmenlearning2026'
param blobContainerName string = 'documents'
param blobName string = 'hello.txt'

var cognitiveServicesOpenAIUserRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
)

var storageBlobDataContributorRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
)

var websiteContributorRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'de139f84-1756-47ae-9be6-808fbbe84772'
)

resource foundryAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  name: foundryResourceName
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2025-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2025-06-01' = {
  name: 'default'
  parent: storageAccount
}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2025-06-01' = {
  name: blobContainerName
  parent: blobService
}

resource appServicePlan 'Microsoft.Web/serverfarms@2025-03-01' = {
  name: appServicePlanName
  location: appServiceLocation
  sku: {
    name: 'F1'
    tier: 'Free'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2025-03-01' = {
  name: webAppName
  location: appServiceLocation
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|${pythonVersion}'
      alwaysOn: false
    }
    httpsOnly: true
  }
}

resource webAppSettings 'Microsoft.Web/sites/config@2025-03-01' = {
  name: 'appsettings'
  parent: webApp
  properties: {
    AZURE_STORAGE_ACCOUNT_NAME: storageAccount.name
    AZURE_STORAGE_CONTAINER_NAME: blobContainer.name
    AZURE_STORAGE_BLOB_NAME: blobName

    AZURE_AI_ENDPOINT: 'https://${foundryResourceName}.openai.azure.com/openai/v1/'
    AZURE_AI_DEPLOYMENT: 'gpt-5-mini-learning'

    SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
  }
}

resource webAppFoundryInferenceRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(foundryAccount.id, webApp.id, cognitiveServicesOpenAIUserRoleDefinitionId)
  scope: foundryAccount
  properties: {
    roleDefinitionId: cognitiveServicesOpenAIUserRoleDefinitionId
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource storageBlobDataRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, webApp.id, storageBlobDataContributorRoleDefinitionId)
  scope: storageAccount
  properties: {
    roleDefinitionId: storageBlobDataContributorRoleDefinitionId
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource jenkinsWebsiteContributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(webApp.id, jenkinsPrincipalId, websiteContributorRoleDefinitionId)
  scope: webApp
  properties: {
    roleDefinitionId: websiteContributorRoleDefinitionId
    principalId: jenkinsPrincipalId
    principalType: 'ServicePrincipal'
  }
}
