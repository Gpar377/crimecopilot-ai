'use client';

import React from 'react';
import { LineChart, ShieldAlert, Zap, AlertCircle } from 'lucide-react';

interface TrendPoint {
  month: string;
  count: number;
}

interface ForecastDetails {
  district: string;
  crime_type: string;
  projected_count: number;
  risk_level: string;
  confidence: number;
  drivers: string[];
  historical_trend: TrendPoint[];
}

interface CrimeForecastProps {
  data: ForecastDetails;
}

export default function CrimeForecast({ data }: CrimeForecastProps) {
  const info = data;
  const trend = info.historical_trend || [];

  // SVG Line Chart calculations
  const svgWidth = 420;
  const svgHeight = 180;
  const padding = 30;

  const maxVal = Math.max(...trend.map(t => t.count), info.projected_count, 10);
  const minVal = 0;

  // Map values to coordinates
  const points = trend.map((t, idx) => {
    const x = padding + (idx / (trend.length)) * (svgWidth - 2 * padding);
    const y = svgHeight - padding - (t.count / maxVal) * (svgHeight - 2 * padding);
    return { x, y, label: t.count, month: t.month.slice(5) }; // just MM
  });

  // Future projected coordinate
  const projectedX = svgWidth - padding;
  const projectedY = svgHeight - padding - (info.projected_count / maxVal) * (svgHeight - 2 * padding);

  // Generate SVG Path
  let linePath = '';
  if (points.length > 0) {
    linePath = `M ${points[0].x} ${points[0].y} ` + points.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ');
  }

  // Projection dotted path
  const lastPoint = points[points.length - 1];
  const projectionPath = lastPoint ? `M ${lastPoint.x} ${lastPoint.y} L ${projectedX} ${projectedY}` : '';

  return (
    <div className="flex flex-col gap-5 w-full">
      {/* Risk Alert Header */}
      <div className={`glass-panel border p-4 rounded-lg flex items-start gap-3 bg-gradient-to-r ${
        info.risk_level === 'HIGH' 
          ? 'from-red-500/10 to-transparent border-red-500/20' 
          : 'from-yellow-500/10 to-transparent border-yellow-500/20'
      }`}>
        <ShieldAlert className={`h-5 w-5 mt-0.5 ${info.risk_level === 'HIGH' ? 'text-red-500 text-glow-red animate-pulse' : 'text-yellow-500'}`} />
        <div className="flex-1">
          <div className="flex justify-between items-center">
            <span className="text-[10px] font-mono uppercase tracking-widest text-[#6b7c93]">30-Day Proactive Risk Forecast</span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
              info.risk_level === 'HIGH' ? 'bg-red-500/10 text-red-400' : 'bg-yellow-500/10 text-yellow-400'
            }`}>
              {info.risk_level} RISK
            </span>
          </div>
          <h3 className="text-sm font-bold font-sans text-[#f1f3f5] mt-1">{info.crime_type.replace('_', ' ').toUpperCase()} IN {info.district.toUpperCase()}</h3>
          <p className="text-[11px] text-[#9eb1c2] font-sans mt-1">
            Projections indicate a potential volume of <strong className="text-brand-cyan">{info.projected_count} incidents</strong> over the next 30 days.
          </p>
        </div>
      </div>

      {/* SVG Trend Line Chart */}
      <div className="glass-panel border border-white/5 p-4 rounded-lg flex flex-col gap-3">
        <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#f1f3f5] flex items-center gap-1.5">
          <LineChart className="h-4 w-4 text-brand-cyan" /> Historical Crime Trends & Projection
        </span>

        <div className="bg-[#090b0e] border border-white/5 rounded p-2 flex items-center justify-center relative">
          <svg width={svgWidth} height={svgHeight} className="overflow-visible select-none">
            {/* Grids */}
            <line x1={padding} y1={svgHeight - padding} x2={svgWidth - padding} y2={svgHeight - padding} stroke="#ffffff" strokeOpacity={0.08} />
            <line x1={padding} y1={padding} x2={padding} y2={svgHeight - padding} stroke="#ffffff" strokeOpacity={0.08} />

            {/* Render lines */}
            {linePath && (
              <path d={linePath} fill="none" stroke="#38ef7d" strokeWidth={2.5} />
            )}
            
            {/* Render projection line */}
            {projectionPath && (
              <path d={projectionPath} fill="none" stroke="#ef4444" strokeWidth={2} strokeDasharray="4 4" />
            )}

            {/* Historical points */}
            {points.map((p, idx) => (
              <g key={idx}>
                <circle cx={p.x} cy={p.y} r={4} fill="#38ef7d" stroke="#090b0e" strokeWidth={1} />
                <text x={p.x} y={p.y - 8} fill="#9eb1c2" fontSize={8} fontFamily="monospace" textAnchor="middle">{p.label}</text>
                <text x={p.x} y={svgHeight - 12} fill="#6b7c93" fontSize={8} fontFamily="monospace" textAnchor="middle">{p.month}</text>
              </g>
            ))}

            {/* Projected point */}
            <g>
              <circle cx={projectedX} cy={projectedY} r={5} fill="#ef4444" stroke="#090b0e" strokeWidth={1.5} className="animate-pulse" />
              <text x={projectedX} y={projectedY - 8} fill="#ef4444" fontSize={9} fontFamily="monospace" fontWeight="bold" textAnchor="middle">{info.projected_count}</text>
              <text x={projectedX} y={svgHeight - 12} fill="#ef4444" fontSize={8} fontFamily="monospace" textAnchor="middle">Proj</text>
            </g>
          </svg>
        </div>
      </div>

      {/* Confidence Level */}
      <div className="glass-panel border border-white/5 p-4 rounded-lg flex items-center justify-between">
        <div className="flex flex-col gap-0.5">
          <span className="text-xs font-mono font-bold text-[#f1f3f5]">Model Confidence Index</span>
          <span className="text-[10px] text-[#6b7c93] font-sans">Based on historical variance parameters</span>
        </div>
        <div className="flex items-center gap-3">
          {/* Progress bar circular equivalent */}
          <div className="text-right">
            <span className="text-lg font-bold font-mono text-brand-cyan text-glow-cyan">{info.confidence}%</span>
          </div>
        </div>
      </div>

      {/* Primary Risk Drivers */}
      <div className="glass-panel border border-white/5 p-4 rounded-lg flex flex-col gap-3">
        <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#f1f3f5] flex items-center gap-1.5">
          <Zap className="h-4 w-4 text-brand-yellow" /> Primary Risk Drivers
        </span>
        <div className="flex flex-col gap-2.5">
          {info.drivers.map((d, idx) => (
            <div key={idx} className="flex gap-2.5 items-start">
              <AlertCircle className="h-4 w-4 text-brand-yellow shrink-0 mt-0.5" />
              <span className="text-[11px] text-[#9eb1c2] leading-relaxed font-sans">{d}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
