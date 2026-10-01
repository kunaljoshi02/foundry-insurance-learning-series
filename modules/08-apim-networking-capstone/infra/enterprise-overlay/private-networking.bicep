// Optional enterprise overlay for Module 08.
// This file is intentionally SEPARATE from foundation/bicep/main.bicep.
// It demonstrates a gated VNet + subnet + private endpoint pattern without
// changing the public learning foundation used by Modules 01-07.

targetScope = 'resourceGroup'

@description('DISABLED BY DEFAULT. Set to true only when you are intentionally reviewing the enterprise private-networking overlay for Module 08.')
param enableEnterpriseOverlay bool = false

@description('Azure region for the optional overlay resources.')
param location string = resourceGroup().location

@description('Short, safe prefix for overlay resource names.')
param overlayNamePrefix string = 'capstone'

@description('Existing Foundry account resource ID to front with a private endpoint.')
param foundryAccountResourceId string = '<foundry-account-resource-id>'

@description('Address space for the optional enterprise overlay VNet.')
param virtualNetworkAddressSpace string = '10.20.0.0/16'

@description('Address prefix for the delegated/agent subnet used by the private networking pattern.')
param agentSubnetAddressPrefix string = '10.20.1.0/24'

@description('Address prefix for the private endpoint subnet.')
param privateEndpointSubnetAddressPrefix string = '10.20.2.0/24'

@description('Private DNS zone used by the Foundry private endpoint.')
param privateDnsZoneName string = 'privatelink.cognitiveservices.azure.com'

@description('Tags applied only to optional overlay resources.')
param tags object = {
  course: 'foundry-insurance-learning-series'
  module: '08-apim-networking-capstone'
  overlay: 'enterprise'
}

var virtualNetworkName = '${overlayNamePrefix}-enterprise-vnet'
var privateEndpointName = '${overlayNamePrefix}-foundry-pe'
var privateDnsZoneLinkName = '${overlayNamePrefix}-dns-link'

resource enterpriseVnet 'Microsoft.Network/virtualNetworks@2024-05-01' = if (enableEnterpriseOverlay) {
  name: virtualNetworkName
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        virtualNetworkAddressSpace
      ]
    }
    subnets: [
      {
        name: 'agent-subnet'
        properties: {
          addressPrefix: agentSubnetAddressPrefix
        }
      }
      {
        name: 'private-endpoint-subnet'
        properties: {
          addressPrefix: privateEndpointSubnetAddressPrefix
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
    ]
  }
}

resource foundryPrivateDnsZone 'Microsoft.Network/privateDnsZones@2024-06-01' = if (enableEnterpriseOverlay) {
  name: privateDnsZoneName
  location: 'global'
  tags: tags
}

resource privateDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = if (enableEnterpriseOverlay) {
  parent: foundryPrivateDnsZone
  name: privateDnsZoneLinkName
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: enterpriseVnet.id
    }
  }
}

resource foundryPrivateEndpoint 'Microsoft.Network/privateEndpoints@2024-05-01' = if (enableEnterpriseOverlay) {
  name: privateEndpointName
  location: location
  tags: tags
  properties: {
    subnet: {
      id: '${enterpriseVnet.id}/subnets/private-endpoint-subnet'
    }
    privateLinkServiceConnections: [
      {
        name: 'foundry-account-connection'
        properties: {
          privateLinkServiceId: foundryAccountResourceId
          groupIds: [
            'account'
          ]
          requestMessage: 'Optional enterprise overlay for the APIM + networking capstone.'
        }
      }
    ]
  }
}

resource privateEndpointDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = if (enableEnterpriseOverlay) {
  parent: foundryPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'foundry-dns'
        properties: {
          privateDnsZoneId: foundryPrivateDnsZone.id
        }
      }
    ]
  }
}

output enterpriseOverlayApplied bool = enableEnterpriseOverlay
output enterpriseVirtualNetworkId string = enableEnterpriseOverlay ? enterpriseVnet.id : ''
output enterprisePrivateEndpointId string = enableEnterpriseOverlay ? foundryPrivateEndpoint.id : ''
output operatorReminder string = 'This overlay is intentionally separate from the public foundation. Review and deploy it only with explicit approval.'
