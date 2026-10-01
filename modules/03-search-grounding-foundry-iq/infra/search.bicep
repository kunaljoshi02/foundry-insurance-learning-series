// Module 03 — Azure AI Search service for grounding the policy corpus.
// This template intentionally provisions only the Search service. The Search index is created
// by src/build_search_index.py, and the Foundry connection / agent tool attachment are handled
// by src/connect_search_to_agent.py (or directly in the portal).
//
// Reference pattern for a connection resource:
//   Microsoft.CognitiveServices/accounts/connections
// See Microsoft Learn and the microsoft-foundry/foundry-samples connection templates for the
// exact current shape. We keep connection creation out of this Bicep file because it depends on
// the learner's existing Foundry account/project and can vary by authentication approach.

targetScope = 'resourceGroup'

@description('Name of the Azure AI Search service for Module 03.')
@minLength(2)
param searchServiceName string

@description('Azure region for the Search service. Use the same region family as your Foundry foundation when practical.')
param location string = resourceGroup().location

@description('Search SKU for the teaching lab. Basic is sufficient for this module.')
@allowed([
  'basic'
])
param skuName string = 'basic'

@description('Tags used by deploy/cleanup scripts to identify module-owned assets.')
param tags object = {
  course: 'foundry-insurance-learning-series'
  module: '03-search-grounding-foundry-iq'
}

resource searchService 'Microsoft.Search/searchServices@2025-02-01-preview' = {
  name: searchServiceName
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  properties: {
    hostingMode: 'default'
    replicaCount: 1
    partitionCount: 1
    publicNetworkAccess: 'enabled'
    disableLocalAuth: false
  }
}

output searchServiceName string = searchService.name
output searchServiceId string = searchService.id
output searchServiceEndpoint string = searchService.properties.endpoint
