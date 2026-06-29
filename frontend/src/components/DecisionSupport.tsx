'use client';

import React, { useState } from 'react';
import { ClipboardList, Clock, ShieldAlert, CheckSquare, Square, CheckCircle2 } from 'lucide-react';

interface Suspect {
  name: string;
  role: string;
  risk_score: number;
  gang: string | null;
}

interface CaseDetails {
  fir_number: string;
  crime_type: string;
  district: string;
  location_description: string;
  date_filed: string;
  status: string;
  modus_operandi: string;
  case_description: string;
  timeline: { time: string; event: string }[];
  leads: string[];
  suspects: Suspect[];
}

interface DecisionSupportProps {
  data: CaseDetails;
}

export default function DecisionSupport({ data }: DecisionSupportProps) {
  const [checkedLeads, setCheckedLeads] = useState<Record<number, boolean>>({});
  const info = data;

  const toggleLead = (index: number) => {
    setCheckedLeads(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const completedCount = Object.values(checkedLeads).filter(Boolean).length;
  const progressPct = info.leads.length > 0 ? (completedCount / info.leads.length) * 100 : 0;

  return (
    <div className="flex flex-col gap-5 w-full">
      {/* Case Header Details */}
      <div className="glass-panel border border-white/5 p-4 rounded-lg flex flex-col gap-2">
        <div className="flex justify-between items-start border-b border-white/5 pb-2">
          <div>
            <span className="text-[10px] font-mono text-brand-yellow uppercase tracking-widest">Official Lead Sheet</span>
            <h3 className="text-sm font-bold font-sans text-[#f1f3f5]">{info.fir_number}</h3>
          </div>
          <span className="px-2 py-0.5 rounded bg-brand-yellow/10 border border-brand-yellow/30 text-[9px] font-mono text-brand-yellow uppercase">
            {info.status}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-[#9eb1c2]">
          <div>Type: <strong className="text-[#f1f3f5]">{info.crime_type}</strong></div>
          <div>District: <strong className="text-[#f1f3f5]">{info.district}</strong></div>
          <div className="col-span-2">Loc: <strong className="text-[#f1f3f5]">{info.location_description}</strong></div>
        </div>
        <p className="text-[11px] text-[#6b7c93] italic font-sans border-t border-white/5 pt-2 mt-1">
          &ldquo;{info.case_description.slice(0, 150)}...&rdquo;
        </p>
      </div>

      {/* Incident Occurrence Timeline */}
      <div className="glass-panel border border-white/5 p-4 rounded-lg flex flex-col gap-3">
        <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#f1f3f5] flex items-center gap-1.5">
          <Clock className="h-4 w-4 text-brand-cyan" /> Incident Chronology
        </span>
        <div className="flex flex-col gap-3 pl-2 border-l border-white/10 mt-1 ml-2">
          {info.timeline.map((item, idx) => (
            <div key={idx} className="relative flex flex-col gap-0.5 pl-4">
              <div className="absolute -left-[21px] top-1 h-2 w-2 rounded-full bg-brand-cyan shadow-sm shadow-brand-cyan" />
              <span className="text-[9px] font-mono text-brand-cyan font-bold">{item.time}</span>
              <span className="text-[11px] font-sans text-[#9eb1c2]">{item.event}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Accused Suspect Risk Log */}
      {info.suspects.length > 0 && (
        <div className="glass-panel border border-white/5 p-4 rounded-lg flex flex-col gap-3">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#f1f3f5] flex items-center gap-1.5">
            <ShieldAlert className="h-4 w-4 text-brand-red" /> Suspect Risk Index
          </span>
          <div className="flex flex-col gap-2">
            {info.suspects.map((s, idx) => (
              <div key={idx} className="flex justify-between items-center bg-white/2 border border-white/5 p-2 rounded">
                <div className="flex flex-col">
                  <span className="text-xs font-sans font-bold text-[#f1f3f5]">{s.name}</span>
                  <span className="text-[9px] font-mono text-[#6b7c93] uppercase">Role: {s.role} | Gang: {s.gang || 'None'}</span>
                </div>
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold ${
                  s.risk_score > 75 ? 'bg-red-500/10 border border-red-500/30 text-red-400' : 'bg-yellow-500/10 border border-yellow-500/30 text-yellow-400'
                }`}>
                  Risk: {s.risk_score}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Interactive Recommended Investigation Leads Checklist */}
      <div className="glass-panel border border-white/5 p-4 rounded-lg flex flex-col gap-3">
        <div className="flex justify-between items-center">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#f1f3f5] flex items-center gap-1.5">
            <ClipboardList className="h-4 w-4 text-brand-yellow" /> Recommended leads
          </span>
          <span className="text-[9px] font-mono text-[#6b7c93]">
            {completedCount}/{info.leads.length} Done
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-white/5 h-1 rounded overflow-hidden">
          <div 
            className="bg-brand-yellow h-full transition-all duration-300"
            style={{ width: `${progressPct}%` }}
          />
        </div>

        <div className="flex flex-col gap-2 mt-1">
          {info.leads.map((lead, idx) => {
            const isChecked = !!checkedLeads[idx];
            return (
              <div 
                key={idx}
                onClick={() => toggleLead(idx)}
                className={`flex gap-3 items-start p-2.5 rounded border transition-all cursor-pointer select-none ${
                  isChecked 
                    ? 'bg-brand-yellow/5 border-brand-yellow/20 text-[#6b7c93] line-through' 
                    : 'bg-white/2 border-white/5 hover:border-white/10 text-[#9eb1c2] hover:text-[#f1f3f5]'
                }`}
              >
                {isChecked ? (
                  <CheckCircle2 className="h-4 w-4 text-brand-yellow shrink-0 mt-0.5" />
                ) : (
                  <Square className="h-4 w-4 text-[#6b7c93] shrink-0 mt-0.5" />
                )}
                <span className="text-[11px] leading-relaxed font-sans">{lead}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
