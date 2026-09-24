export interface DecisionResult {
  route: string;
  is_emergency: boolean;
  severity_score: number;
  latency_us: number;
  execution_mode: string;
  cloud_dependency: boolean;
}

export interface QueryResult {
  answer: string;
  latency_us: number;
  latency_ms: number;
  multipliers_used: number;
  hallucination_rate: string;
  memory_state: string;
}

export declare class BrahmandEngine {
  constructor();
  init(): Promise<boolean>;
  evaluateState(stateText: string): DecisionResult;
  query(prompt: string): QueryResult;
  learn(domain: string, text: string): number;
}

export default BrahmandEngine;
