// Reusable RBAC role assignment module. Modules call this instead of duplicating
// role-assignment boilerplate. Scope is whatever resource ID is passed in.
targetScope = 'resourceGroup'

@description('Resource ID to scope the role assignment to (e.g. a Foundry project, Search service, or Storage account).')
param targetResourceId string

@description('Built-in role definition GUID (not the full resource ID) — see https://learn.microsoft.com/azure/role-based-access-control/built-in-roles')
param roleDefinitionId string

@description('Principal (object) ID to assign the role to.')
param principalId string

@allowed([
  'User'
  'ServicePrincipal'
  'Group'
])
param principalType string = 'User'

resource targetResource 'Microsoft.Resources/resources@2024-11-01' existing = {
  name: last(split(targetResourceId, '/'))
  scope: resourceGroup()
}

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(targetResourceId, principalId, roleDefinitionId)
  scope: targetResource
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionId)
    principalId: principalId
    principalType: principalType
  }
}

output roleAssignmentId string = roleAssignment.id

// Common built-in role GUIDs referenced across modules (documented here so module Bicep
// files don't need to hardcode magic strings without context):
//   Azure AI User                 53ca6127-db72-4b80-b1b0-d745d6d5456d
//   Azure AI Project Manager      eadc314b-1a2d-4efa-be10-5d325db5065e
//   Search Index Data Reader      1407120a-92aa-4202-b7e9-c0e197c71c8f
//   Search Index Data Contributor 8ebe5a00-799e-43f5-93ac-243d3dce84a7
//   Search Service Contributor    7ca78c08-252a-4471-8644-bb5ff32d4ba0
//   Cognitive Services User       a97b65f3-24c7-4388-baec-2e87135dc908
//   Storage Blob Data Reader      2a2b9908-6ea1-4ae2-8e65-a410df84e7d1
