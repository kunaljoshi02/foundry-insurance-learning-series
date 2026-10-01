// Microsoft Foundry Insurance Learning Series — shared public foundation.
// Deploys ONE public Azure AI Foundry (AIServices) account + project + a configurable
// chat model deployment, with base RBAC for a learner identity. Every module in this
// curriculum builds additively on top of this foundation; nothing here is VNet-injected
// or APIM-fronted (that is covered, opt-in, in module 08's enterprise overlay).
//
// This template is NOT deployed by this repository automatically. Run it yourself with
// `foundation/scripts/deploy.ps1` (or `az deployment group create`) after completing the
// preflight checks in `foundation/scripts/preflight.ps1`.

targetScope = 'resourceGroup'

@description('Short, unique-ish name prefix for all resources (lowercase alphanumeric, 3-12 chars). A random suffix is appended.')
@minLength(3)
@maxLength(12)
param namePrefix string = 'fdyins'

@description('Azure region for all resources. Must support Azure AI Foundry + the chosen model.')
param location string = resourceGroup().location

@description('Principal (object) ID of the learner/operator to grant Foundry RBAC roles to. Leave empty to skip RBAC assignment.')
param principalId string = ''

@description('Principal type for the RBAC assignment above.')
@allowed([
  'User'
  'ServicePrincipal'
  'Group'
])
param principalType string = 'User'

@description('Chat model to deploy (see https://learn.microsoft.com/azure/ai-foundry/concepts/models for availability by region).')
param chatModelName string = 'gpt-4o-mini'

@description('Model format/publisher, almost always OpenAI for first-party chat models.')
param chatModelFormat string = 'OpenAI'

@description('Chat model version. Pin to a specific version for reproducibility; see the portal Model catalog for current values.')
param chatModelVersion string = '2024-07-18'

@description('Deployment SKU name for the model (Standard, GlobalStandard, etc.).')
param chatModelSkuName string = 'GlobalStandard'

@description('Deployment capacity in units of 1,000 TPM, subject to regional quota.')
@minValue(1)
param chatModelCapacity int = 10

@description('Tags applied to every resource so cleanup scripts can safely identify module/course-owned assets.')
param tags object = {
  course: 'foundry-insurance-learning-series'
  owner: 'foundation'
}

var uniqueSuffix = uniqueString(resourceGroup().id, namePrefix)
var accountName = toLower('${namePrefix}fdy${uniqueSuffix}')
var projectName = toLower('${namePrefix}proj${uniqueSuffix}')

// Azure AI Foundry account (kind: AIServices). Public network access is intentionally
// enabled — this is the shared PUBLIC foundation. Module 08's enterprise overlay shows
// the private-networking variant as an explicitly gated, disabled-by-default add-on.
resource foundryAccount 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: accountName
  location: location
  tags: tags
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: accountName
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
    allowProjectManagement: true
  }
}

// Foundry project (child resource) — the unit learners interact with in the portal.
resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' = {
  parent: foundryAccount
  name: projectName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: 'Foundry Insurance Learning Series'
    description: 'Shared public foundation project for the 8-session Foundry insurance curriculum.'
  }
}

// Configurable chat model deployment shared by modules 01-07 (module 08 may add its own
// BYOM/APIM-fronted connection in the enterprise overlay).
resource chatModelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: foundryAccount
  name: chatModelName
  sku: {
    name: chatModelSkuName
    capacity: chatModelCapacity
  }
  properties: {
    model: {
      format: chatModelFormat
      name: chatModelName
      version: chatModelVersion
    }
    raiPolicyName: 'Microsoft.DefaultV2'
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
}

// Base RBAC: Azure AI User lets a learner/operator use the project (chat, agents, threads)
// without granting account-level management permissions.
var azureAiUserRoleId = '53ca6127-db72-4b80-b1b0-d745d6d5456d'

resource learnerRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(principalId)) {
  name: guid(foundryProject.id, principalId, azureAiUserRoleId)
  scope: foundryProject
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', azureAiUserRoleId)
    principalId: principalId
    principalType: principalType
  }
}

output foundryAccountName string = foundryAccount.name
output foundryAccountId string = foundryAccount.id
output foundryProjectName string = foundryProject.name
output foundryProjectId string = foundryProject.id
output foundryEndpoint string = foundryAccount.properties.endpoint
output chatModelDeploymentName string = chatModelDeployment.name
output principalAssigned bool = !empty(principalId)
