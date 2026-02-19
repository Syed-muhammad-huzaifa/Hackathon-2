/**
 * Premium status distribution chart with gradients
 *
 * @spec specs/003-todo-frontend/spec.md (FR-029, US4)
 */

'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Card } from '@/components/ui/card';

interface StatusChartProps {
  data: {
    pending: number;
    'in-progress': number;
    completed: number;
  };
}

const COLORS = {
  pending: '#64748B',
  'in-progress': '#3B82F6',
  completed: '#10B981',
};

const GRADIENTS = {
  pending: ['#64748B', '#475569'],
  'in-progress': ['#3B82F6', '#2563EB'],
  completed: ['#10B981', '#059669'],
};

export function StatusChart({ data }: StatusChartProps) {
  const chartData = [
    { name: 'Pending', value: data.pending, color: COLORS.pending, id: 'pending' },
    { name: 'In Progress', value: data['in-progress'], color: COLORS['in-progress'], id: 'in-progress' },
    { name: 'Completed', value: data.completed, color: COLORS.completed, id: 'completed' },
  ].filter(item => item.value > 0);

  if (chartData.length === 0) {
    return (
      <Card className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl p-8 backdrop-blur-xl">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
          <div className="w-1 h-6 bg-gradient-to-b from-primary to-secondary rounded-full" />
          Status Distribution
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
        <div className="w-1 h-6 bg-gradient-to-b from-primary to-secondary rounded-full" />
        Status Distribution
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <defs>
            {chartData.map((entry) => (
              <linearGradient key={entry.id} id={`gradient-${entry.id}`} x1="0" y1="0" x2="0" y2="1">
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
                fill={`url(#gradient-${entry.id})`}
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
