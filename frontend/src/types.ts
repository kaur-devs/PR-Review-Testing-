export type Operator =
  | 'equals'
  | 'not_equals'
  | 'contains'
  | 'in'
  | 'greater_than';

export interface Rule {
  attribute: string;
  operator: Operator;
  value: string;
}

export interface Flag {
  id: number;
  key: string;
  description: string;
  enabled: boolean;
  rollout_percent: number;
  updated_at: string;
  rules: Rule[];
}

export interface Evaluation {
  user_key: string;
  flags: Record<string, boolean>;
}
