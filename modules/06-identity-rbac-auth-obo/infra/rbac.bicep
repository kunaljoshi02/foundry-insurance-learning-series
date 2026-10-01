targetScope = 'resourceGroup'

@description('Default resource ID scope for module role assignments. Use the Foundry project resource ID unless a role item provides a narrower scopeResourceId override.')
param foundryProjectResourceId string

@description('Principal (object) ID to assign the roles to.')
param principalId string

@allowed([
  'User'
  'ServicePrincipal'
  'Group'
])
param principalType string = 'User'

@description('Roles to assign. Each item must include name and can optionally include scopeResourceId for narrower least-privilege scoping.')
param roles array

var roleDefinitionIds = {
  'Azure AI User': '53ca6127-db72-4b80-b1b0-d745d6d5456d'
  'Azure AI Project Manager': 'eadc314b-1a2d-4efa-be10-5d325db5065e'
  'Search Index Data Reader': '1407120a-92aa-4202-b7e9-c0e197c71c8f'
  'Cognitive Services User': 'a97b65f3-24c7-4388-baec-2e87135dc908'
}

var normalizedRoles = [
  for role in roles: {
    name: role.name
    scopeResourceId: contains(role, 'scopeResourceId') && role.scopeResourceId != '' ? role.scopeResourceId : foundryProjectResourceId
    roleDefinitionId: roleDefinitionIds[role.name]
  }
]

module roleAssignments '../../../shared/bicep/rbac-assignment.bicep' = [
  for role in normalizedRoles: {
    name: 'module06-${uniqueString(role.scopeResourceId, principalId, role.roleDefinitionId)}'
    params: {
      targetResourceId: role.scopeResourceId
      roleDefinitionId: role.roleDefinitionId
      principalId: principalId
      principalType: principalType
    }
  }
]

output assignments array = [
  for (role, i) in normalizedRoles: {
    name: role.name
    scopeResourceId: role.scopeResourceId
    roleAssignmentId: roleAssignments[i].outputs.roleAssignmentId
  }
]
