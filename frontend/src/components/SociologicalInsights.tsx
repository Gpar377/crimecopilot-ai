'use client';

import React, { useState } from 'react';
import { HelpCircle, BarChart3, TrendingUp, Info } from 'lucide-react';

interface DistrictData {
  district: string;
  literacy_rate: number;
  unemployment_rate: number;
  migration_index: number;
  urbanization_score: number;
  median_income_bracket: string;
  crime_count: number;
}

interface SociologicalInsightsProps {
  data: {
    districts: DistrictData[];
  };
}

export default function SociologicalInsights({ data }: SociologicalInsightsProps) {
  const [hoveredDistrict, setHoveredDistrict] = useState<DistrictData | null>(null);
  const districts = data?.districts || [];

  if (districts.length === 0) {
    return (
      <div className="glass-panel p-6 border border-white/5 rounded-lg text-center text-xs font-mono text-[#6b7c93]">
        No sociological records retrieved to plot.
      </div>
    );
  }

  // Find max values for normalization
  const maxCrime = Math.max(...districts.map(d => d.crime_count), 1);
  const maxUnemployment = Math.max(...districts.map(d => d.unemployment_rate), 1);

  // SVG dimensions
  const scatterWidth = 400;
  const scatterHeight = 220;
  const padding = 35;

  return (
    <div className="flex flex-col gap-5 w-full">
      {/* Overview Card */}
      <div className="glass-panel border border-white/5 p-4 rounded-lg bg-gradient-to-r from-brand-cyan/5 to-transparent flex items-start gap-3">
        <Info className="h-4.5 w-4.5 text-brand-cyan mt-0.5" />
        <div className="flex-1">
          <h4 className="text-xs font-bold font-mono uppercase tracking-wider text-brand-cyan">Socio-Economic Crime Correlations</h4>
          <p className="text-[11px] text-[#9eb1c2] font-sans mt-1 leading-relaxed">
            This module compares regional KSP crime density against census indices (literacy, unemployment, and urbanization). Use the interactive charts below to analyze correlation clusters.
          </p>
        </div>
      </div>

      {/* Correlation Bubble Plot (Literacy vs Crime) */}
      <div className="glass-panel border border-white/5 p-5 rounded-lg flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#f1f3f5] flex items-center gap-1.5">
            <TrendingUp className="h-4 w-4 text-brand-cyan" /> 1. Literacy vs. Crime Density
          </span>
          <span className="text-[10px] font-mono text-[#6b7c93]">Interactive Scatter Plot</span>
        </div>

        <div className="relative bg-[#090b0e] border border-white/5 rounded-lg p-2 flex items-center justify-center">
          <svg width={scatterWidth} height={scatterHeight} className="overflow-visible select-none">
            {/* Grid Lines */}
            <line x1={padding} y1={scatterHeight - padding} x2={scatterWidth - padding} y2={scatterHeight - padding} stroke="#ffffff" strokeOpacity={0.08} strokeWidth={1} />
            <line x1={padding} y1={padding} x2={padding} y2={scatterHeight - padding} stroke="#ffffff" strokeOpacity={0.08} strokeWidth={1} />
            
            {/* Grid helpers */}
            <line x1={padding} y1={(scatterHeight - 2 * padding) / 2 + padding} x2={scatterWidth - padding} y2={(scatterHeight - 2 * padding) / 2 + padding} stroke="#ffffff" strokeOpacity={0.03} strokeWidth={1} strokeDasharray="3 3" />
            <line x1={(scatterWidth - 2 * padding) / 2 + padding} y1={padding} x2={(scatterWidth - 2 * padding) / 2 + padding} y2={scatterHeight - padding} stroke="#ffffff" strokeOpacity={0.03} strokeWidth={1} strokeDasharray="3 3" />

            {/* Labels */}
            <text x={scatterWidth / 2} y={scatterHeight - 8} fill="#6b7c93" fontSize={9} fontFamily="monospace" textAnchor="middle">Literacy Rate (%)</text>
            <text x={10} y={scatterHeight / 2} fill="#6b7c93" fontSize={9} fontFamily="monospace" textAnchor="middle" transform={`rotate(-90 10 ${scatterHeight / 2})`}>FIR Volume</text>

            {/* Render Bubbles */}
            {districts.map((d, idx) => {
              // Map x-axis: literacy rate ranges roughly from 60 to 90
              const xMin = 60;
              const xMax = 95;
              const cx = padding + ((d.literacy_rate - xMin) / (xMax - xMin)) * (scatterWidth - 2 * padding);
              
              // Map y-axis: crime count from 0 to maxCrime
              const cy = scatterHeight - padding - (d.crime_count / maxCrime) * (scatterHeight - 2 * padding);
              
              // Radius is scaled by urbanization score (higher score = bigger bubble)
              const r = 6 + (d.urbanization_score / 100) * 12;

              const isHovered = hoveredDistrict?.district === d.district;

              return (
                <g key={idx}>
                  <circle
                    cx={cx}
                    cy={cy}
                    r={r}
                    fill={isHovered ? '#00f2fe' : '#38ef7d'}
                    fillOpacity={isHovered ? 0.8 : 0.4}
                    stroke={isHovered ? '#00f2fe' : '#38ef7d'}
                    strokeWidth={isHovered ? 2 : 1}
                    className="transition-all duration-200 cursor-pointer"
                    onMouseEnter={() => setHoveredDistrict(d)}
                    onMouseLeave={() => setHoveredDistrict(null)}
                  />
                  {/* Small Label on bubble */}
                  {d.crime_count > maxCrime * 0.1 && (
                    <text
                      x={cx}
                      y={cy - r - 4}
                      fill="#9eb1c2"
                      fontSize={8}
                      fontFamily="monospace"
                      textAnchor="middle"
                      pointerEvents="none"
                    >
                      {d.district.split(' ')[0]}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>

          {/* Hover Tooltip Overlay */}
          {hoveredDistrict && (
            <div className="absolute top-2 right-2 bg-[#0d1117] border border-[#00f2fe]/30 rounded p-2.5 shadow-xl font-mono text-[10px] w-[180px] z-10 backdrop-blur-md">
              <div className="text-brand-cyan font-bold border-b border-white/5 pb-1 mb-1">{hoveredDistrict.district}</div>
              <div className="flex justify-between text-[#9eb1c2]">
                <span>Literacy:</span>
                <span className="text-[#f1f3f5]">{hoveredDistrict.literacy_rate}%</span>
              </div>
              <div className="flex justify-between text-[#9eb1c2]">
                <span>Crime Count:</span>
                <span className="text-[#f1f3f5]">{hoveredDistrict.crime_count} FIRs</span>
              </div>
              <div className="flex justify-between text-[#9eb1c2]">
                <span>Unemployment:</span>
                <span className="text-[#f1f3f5]">{hoveredDistrict.unemployment_rate}%</span>
              </div>
              <div className="flex justify-between text-[#9eb1c2]">
                <span>Urbanization:</span>
                <span className="text-[#f1f3f5]">{hoveredDistrict.urbanization_score}/100</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Comparative Bar Chart (Unemployment vs Crime Volume) */}
      <div className="glass-panel border border-white/5 p-5 rounded-lg flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#f1f3f5] flex items-center gap-1.5">
            <BarChart3 className="h-4 w-4 text-brand-yellow" /> 2. Unemployment vs. Property Crimes
          </span>
          <span className="text-[10px] font-mono text-[#6b7c93]">Regional Double-Bar Plot</span>
        </div>

        <div className="bg-[#090b0e] border border-white/5 rounded-lg p-4 flex flex-col gap-3.5">
          {districts.map((d, idx) => {
            // Percent widths for rendering
            const unemploymentPct = (d.unemployment_rate / maxUnemployment) * 100;
            const crimePct = (d.crime_count / maxCrime) * 100;

            return (
              <div key={idx} className="flex flex-col gap-1">
                <div className="flex justify-between items-center text-[10px] font-mono text-[#9eb1c2]">
                  <span className="font-bold text-[#f1f3f5]">{d.district}</span>
                  <span className="text-[9px] text-[#6b7c93]">
                    unemp: <strong className="text-brand-yellow">{d.unemployment_rate}%</strong> | crimes: <strong className="text-brand-cyan">{d.crime_count}</strong>
                  </span>
                </div>
                {/* Visual double bar */}
                <div className="flex flex-col gap-1 w-full bg-white/2 rounded p-1 border border-white/5">
                  {/* Unemployment bar */}
                  <div className="h-2 flex items-center gap-2">
                    <span className="text-[8px] font-mono text-[#6b7c93] w-12 text-right">UNEMP</span>
                    <div className="flex-1 bg-white/3 h-1.5 rounded overflow-hidden">
                      <div 
                        className="bg-brand-yellow h-full rounded transition-all duration-300"
                        style={{ width: `${unemploymentPct}%` }}
                      />
                    </div>
                  </div>
                  {/* Crime bar */}
                  <div className="h-2 flex items-center gap-2">
                    <span className="text-[8px] font-mono text-[#6b7c93] w-12 text-right">CRIMES</span>
                    <div className="flex-1 bg-white/3 h-1.5 rounded overflow-hidden">
                      <div 
                        className="bg-brand-cyan h-full rounded transition-all duration-300"
                        style={{ width: `${crimePct}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
