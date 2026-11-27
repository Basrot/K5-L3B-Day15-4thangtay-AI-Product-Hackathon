export type ReferenceMode = "study" | "lab";
export type PregnancyStatus = "pregnant" | "unknown" | "not_pregnant";
export type RowStatus = "below" | "within" | "above";

export interface CatalogItem {
  code: string;
  name: string;
  unit: string;
  group: string;
}

export interface CBCRowInput {
  analyte: string;
  value: string | null;
  unit: string | null;
  ref_low?: string | null;
  ref_high?: string | null;
  ref_unit?: string | null;
}

export interface CBCReport {
  adult_confirmed: boolean;
  pregnancy_status: PregnancyStatus;
  gestational_age: string;
  reference_mode: ReferenceMode;
  rows: CBCRowInput[];
}

export interface ReferenceSource {
  title: string;
  url?: string | null;
}

export interface AnalysisRow {
  analyte: string;
  value: string;
  unit: string;
  ref_low: string;
  ref_high: string;
  status: RowStatus;
}

export interface AnalysisResult {
  status: string;
  output: string;
  rows?: AnalysisRow[];
  counts?: { below: number; within: number; above: number };
  reference_mode?: ReferenceMode;
  trimester?: number;
  reference_source?: ReferenceSource;
  reference_note?: string;
  sources?: ReferenceSource[];
  issues?: string[];
}

export interface ChatResult {
  status: string;
  output: string;
  analyte?: string;
  reference_mode?: ReferenceMode;
  trimester?: number;
  reference_source?: ReferenceSource;
  reference_note?: string;
  sources?: ReferenceSource[];
  revision?: number;
}

export interface HistoryItem {
  question: string;
  result: ChatResult;
  created_at?: string;
}
