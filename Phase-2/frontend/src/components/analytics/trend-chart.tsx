/**
 * Premium completion trend chart with gradients
 *
 * @spec specs/003-todo-frontend/spec.md (FR-031, US4)
 */

'use client';

import { Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Card } from '@/components/ui/card';

interface TrendChartProps {
  data: {
    date: string;
    completed: number;
  }[];
}

export function TrendChart({ data }: TrendChartProps) {
  if (data.length === 0 || data.every(d => d.completed === 0)) {
    return (
      <Card className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl p-8 backdrop-blur-xl">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
          <div className="w-1 h-6 bg-gradient-to-b from-secondary to-accent rounded-full" />
          Completion Trend (Last 30 Days)
        </h3>
        <div className="h-[300px] flex items-center justify-center text-slate-400">
          No completion data available
        </div>
      </Card>
    );
  }

  // Format dates for display (show only every 5th date to avoid crowding)
  const formattedData = data.map((item, index) => ({
    ...item,
    displayDate: index % 5 === 0 ? new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '',
  }));

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: { value: number; payload: { date: string } }[] }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl p-3 backdrop-blur-xl">
          <p className="text-sm text-slate-400">
            {new Date(payload[0].payload.date).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            })}
          </p>
          <p className="text-lg font-bold text-primary">
            {payload[0].value} completed
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl p-8 backdrop-blur-xl hover:scale-[1.005] transition-all duration-300">
      <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
        <div className="w-1 h-6 bg-gradient-to-b from-secondary to-accent rounded-full" />
        Completion Trend (Last 30 Days)
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={formattedData}>
          <defs>
            <linearGradient id="colorCompleted" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#8B5CF6" stopOpacity={0.4} />
              <stop offset="100%" stopColor="#8B5CF6" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="displayDate"
            stroke="rgba(255,255,255,0.3)"
            tick={{ fill: '#94A3B8', fontSize: 12 }}
            tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
          />
          <YAxis
            stroke="rgba(255,255,255,0.3)"
            tick={{ fill: '#94A3B8', fontSize: 12 }}
            tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="completed"
            stroke="#8B5CF6"
            strokeWidth={3}
            fill="url(#colorCompleted)"
            animationBegin={0}
            animationDuration={1000}
            animationEasing="ease-out"
          />
          <Line
            type="monotone"
            dataKey="completed"
            stroke="#8B5CF6"
            strokeWidth={3}
            dot={{ fill: '#8B5CF6', r: 4, strokeWidth: 2, stroke: '#1E293B' }}
            activeDot={{ r: 6, strokeWidth: 2, stroke: '#1E293B' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
}
