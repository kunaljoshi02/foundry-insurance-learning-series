using 'main.bicep'

// Copy this file's values from your own `.env` (see repo root `.env.example`).
// Do not commit a filled-in copy with real names/IDs — this file intentionally
// contains only placeholders.

param namePrefix = '<short-prefix>'
param location = '<azure-region>'
param principalId = '<your-entra-object-id>'
param principalType = 'User'
param chatModelName = 'gpt-4o-mini'
param chatModelFormat = 'OpenAI'
param chatModelVersion = '<model-version>'
param chatModelSkuName = 'GlobalStandard'
param chatModelCapacity = 10
