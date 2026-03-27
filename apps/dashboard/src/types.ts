export type Direction = 'in' | 'out';
export type VehicleType = 'motorbike' | 'car';

export interface VehicleEvent {
  id: string;
  camera_id: string;
  timestamp: string;
  direction: Direction;
  vehicle_type: VehicleType;
  track_id: string;
  plate_text: string | null;
  confidence: number | null;
  snapshot_url: string | null;
}

export interface RealtimeStats {
  total_in: number;
  total_out: number;
  ocr_success_rate: number;
}

export interface Account {
  plate_text: string;
  balance_vnd: number;
}
