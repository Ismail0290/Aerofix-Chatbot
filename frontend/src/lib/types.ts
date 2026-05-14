export type Device = {
  id: string;
  model_number?: string;
  building_type?: string;
  current_status?: string;
  tonnage?: number;
  installation_date?: string;
  last_service_date?: string;
  priority_level?: string;
  [key: string]: unknown;
};

export type IotLog = {
  device_id?: string;
  timestamp?: string;
  compressor_frequency?: number | null;
  power_consumption?: number | null;
  error_code?: string | null;
  refrigerant_pressure?: number | null;
  [key: string]: unknown;
};

export type PriorityTicket = {
  device_id: string;
  model: string;
  building: string;
  error_code: string;
  priority_score: number;
};

export type DevicesResponse = { devices: Device[] };
export type LatestLogsResponse = { device_id: string; logs: IotLog[] };
export type FailuresResponse = { failure_counts: Record<string, number> };
export type ContextResponse = { device_id: string; context: string };
export type PriorityResponse = { tickets: PriorityTicket[] };
