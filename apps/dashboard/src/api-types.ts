export type Direction = 'in' | 'out';
export type VehicleType = 'motorbike' | 'car';
export type OcrStatus = 'success' | 'partial' | 'failed';
export type TransactionType = 'init' | 'event_charge' | 'manual_adjust';

export interface EventIn {
  camera_id: string;
  timestamp: string;
  direction: Direction;
  vehicle_type: VehicleType;
  track_id: string;
  plate_text?: string | null;
  confidence?: number | null;
  snapshot_url?: string | null;
}

export interface EventOut extends EventIn {
  id: string;
}

export interface PlateReadOut {
  id: string;
  event_id: string;
  plate_text: string | null;
  confidence: number | null;
  snapshot_url: string | null;
  crop_url: string | null;
  ocr_status: OcrStatus;
}

export interface AccountOut {
  plate_text: string;
  balance_vnd: number;
}

export interface TransactionOut {
  id: string;
  account_id: string;
  event_id: string | null;
  amount_vnd: number;
  balance_after_vnd: number;
  type: TransactionType;
  created_at: string;
}

export interface RealtimeStatOut {
  total_in: number;
  total_out: number;
  ocr_success_rate: number;
}

export interface TrafficStatOut {
  bucket: string;
  total_in: number;
  total_out: number;
}

export interface OcrRateOut {
  success_rate: number;
}

export interface ErrorOut {
  detail: string;
}
