import { HubConnectionBuilder, LogLevel } from '@microsoft/signalr';

// Load backend URL from config
import backendConfig from './config';

const connection = new HubConnectionBuilder()
  .withUrl(`${backendConfig.BACKEND_URL}/signalr`)
  .configureLogging(LogLevel.Information)
  .build();

export default connection;
