// Azure Bicep template for AnyStockAI resources
// Replace parameter values with your actual resource names and settings

param location string = 'australiaeast'
param sqlAdmin string
param sqlPassword string

resource sqlServer 'Microsoft.Sql/servers@2022-02-01-preview' = {
  name: 'anystockai-sqlserver'
  location: location
  properties: {
    administratorLogin: sqlAdmin
    administratorLoginPassword: sqlPassword
  }
}

resource sqlDb 'Microsoft.Sql/servers/databases@2022-02-01-preview' = {
  name: '${sqlServer.name}/anystockai-db'
  location: location
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
  }
}

resource blobStorage 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: 'anystockaiblob'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: 'anystockai-plan'
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
}

resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: 'anystockai-webapp'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
  }
}

resource signalr 'Microsoft.SignalRService/SignalR@2022-08-01' = {
  name: 'anystockai-signalr'
  location: location
  sku: {
    name: 'Standard_S1'
    tier: 'Standard'
  }
}
