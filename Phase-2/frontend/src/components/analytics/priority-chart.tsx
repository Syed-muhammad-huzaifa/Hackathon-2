/**
 * Premium priority distribution chart with gradients
 *
 * @spec specs/003-todo-frontend/spec.md (FR-030, US4)
 */

'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Card } from '@/components/ui/card';

interface PriorityChartProps {
  data: {
    low: number;
    medium: number;
    high: number;
  };
}

const COLORS = {
  low: '#3B82F6',
  medium: '#F59E0B',
  high: '#EF4444',
};

const GRADIENTS = {
  low: ['#3B82F6', '#2563EB'],
  medium: ['#F59E0B', '#D97706'],
  high: ['#EF4444', '#DC2626'],
};

export function PriorityChart({ data }: PriorityChartProps) {
  const chartData = [
    { name: 'Low', value: data.low, color: COLORS.low, id: 'low' },
    { name: 'Medium', value: data.medium, color: COLORS.medium, id: 'medium' },
    { name: 'High', value: data.high, color: COLORS.high, id: 'high' },
  ].filter(item => item.value > 0);

  if (chartData.length === 0) {
    return (
      <Card className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl p-8 backdrop-blur-xl">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
          <div className="w-1 h-6 bg-gradient-to-b from-accent to-primary rounded-full" />
          Priority Distribution
        </h3>
        <div className="h-[300px] flex items-center justify-center text-slate-400">
          No data available
        </div>
      </Card>
    );
  }

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: { name: string; value: number; payload: { color: string } }[] }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl p-3 backdrop-blur-xl">
          <p className="text-sm font-semibold">{payload[0].name}</p>
          <p className="text-lg font-bold" style={{ color: payload[0].payload.color }}>
            {payload[0].value} tasks
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl p-8 backdrop-blur-xl hover:scale-[1.01] transition-all duration-300">
      <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
        <div className="w-1 h-6 bg-gradient-to-b from-accent to-primary rounded-full" />
        Priority Distribution
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <defs>
            {chartData.map((entry) => (
              <linearGradient key={entry.id} id={`gradient-priority-${entry.id}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={GRADIENTS[entry.id as keyof typeof GRADIENTS][0]} />
                <stop offset="100%" stopColor={GRADIENTS[entry.id as keyof typeof GRADIENTS][1]} />
              </linearGradient>
            ))}
          </defs>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
            outerRadius={100}
            innerRadius={60}
            fill="#8884d8"
            dataKey="value"
            animationBegin={0}
            animationDuration={800}
            animationEasing="ease-out"
          >
            {chartData.map((entry) => (
              <Cell
                key={`cell-${entry.id}`}
                fill={`url(#gradient-priority-${entry.id})`}
                stroke="rgba(255,255,255,0.1)"
                strokeWidth={2}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={36}
            iconType="circle"
            formatter={(value) => <span className="text-slate-300">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  );
}
