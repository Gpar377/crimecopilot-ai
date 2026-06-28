'use client';

import React from 'react';
import { 
  User, AlertTriangle, Phone, CreditCard, Car, 
  Calendar, Shield, MapPin, Grid, ShieldAlert 
} from 'lucide-react';

interface OffenderProfileProps {
  data: {
    accused_id: string;
    name: string;
    age: number;
    gender: string;
    address: string;
    risk_score: number;
    gang_name: string | null;
    phones: string[];
    bank_accounts: Array<{
      bank_name: string;
      account_number_hash: string;
    }>;
    vehicles: Array<{
      registration_number: string;
      type: string;
    }>;
    history: Array<{
      fir_number: string;
      crime_type: string;
      district: string;
      role: string;
      date_filed: string;
      status: string;
    }>;
  };
}

export default function OffenderProfile({ data }: OffenderProfileProps) {
  // Determine risk level and colors
  const getRiskDetails = (score: number) => {
    if (score >= 70) return { text: 'HIGH RISK', color: 'text-red-500', stroke: '#ef4444', bg: 'bg-red-500/10', border: 'border-red-500/20' };
    if (score >= 40) return { text: 'MODERATE RISK', color: 'text-yellow-500', stroke: '#eab308', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20' };
    return { text: 'LOW RISK', color: 'text-emerald-500', stroke: '#10b981', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' };
  };

  const risk = getRiskDetails(data.risk_score);
  
  // Calculate SVG dash offset for circular gauge
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (data.risk_score / 100) * circumference;

  return (
    <div className="glass-panel rounded-lg p-5 flex flex-col gap-6 border border-white/5 bg-[#0a0d11]/40 overflow-y-auto max-h-[550px] scrollbar">
      
      {/* Header Profile Section */}
      <div className="flex items-center justify-between border-b border-white/5 pb-4">
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-[#9eb1c2]">
            <User className="h-6 w-6" />
          </div>
          <div>
            <h3 className="font-bold text-base text-[#f1f3f5] leading-snug">{data.name}</h3>
            <span className="text-[10px] font-mono uppercase tracking-widest text-[#6b7c93]">
              Offender ID: {data.accused_id}
            </span>
          </div>
        </div>

        {/* Circular Risk Gauge */}
        <div className="relative flex items-center justify-center h-16 w-16 select-none">
          <svg className="w-full h-full transform -rotate-90">
            {/* Background circle */}
            <circle
              cx="32"
              cy="32"
              r={radius}
              stroke="rgba(255,255,255,0.05)"
              strokeWidth="5"
              fill="transparent"
            />
            {/* Animated gauge circle */}
            <circle
              cx="32"
              cy="32"
              r={radius}
              stroke={risk.stroke}
              strokeWidth="5"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute flex flex-col items-center justify-center">
            <span className="text-xs font-mono font-bold text-glow-yellow">{data.risk_score}</span>
            <span className="text-[6px] uppercase font-mono text-[#6b7c93]">Risk</span>
          </div>
        </div>
      </div>

      {/* Stats Summary Grid */}
      <div className="grid grid-cols-2 gap-3 text-xs font-mono">
        <div className="p-3 rounded-lg bg-white/2 border border-white/5 flex flex-col gap-1">
          <span className="text-[9px] text-[#6b7c93] uppercase">Demographics</span>
          <span className="text-[#f1f3f5]">{data.age} yrs • {data.gender}</span>
        </div>
        <div className={`p-3 rounded-lg border flex flex-col gap-1 ${risk.bg} ${risk.border}`}>
          <span className="text-[9px] text-[#6b7c93] uppercase">Risk Category</span>
          <span className={`font-bold ${risk.color}`}>{risk.text}</span>
        </div>
        <div className="p-3 rounded-lg bg-white/2 border border-white/5 flex flex-col gap-1 col-span-2">
          <span className="text-[9px] text-[#6b7c93] uppercase flex items-center gap-1">
            <MapPin className="h-3 w-3" /> Registered Address
          </span>
          <span className="text-[#9eb1c2] font-sans">{data.address}</span>
        </div>
        {data.gang_name && (
          <div className="p-3 rounded-lg bg-red-500/5 border border-red-500/10 flex flex-col gap-1 col-span-2">
            <span className="text-[9px] text-red-400 uppercase flex items-center gap-1">
              <ShieldAlert className="h-3 w-3" /> Syndicate & Gang Affiliation
            </span>
            <span className="text-red-400 font-bold tracking-wide uppercase text-[10px]">
              {data.gang_name} Gang
            </span>
          </div>
        )}
      </div>

      {/* Registered Phone Numbers & Accounts Cards */}
      <div className="flex flex-col gap-4">
        
        {/* Contact Links */}
        <div className="flex flex-col gap-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-[#6b7c93] flex items-center gap-1.5">
            <Phone className="h-3.5 w-3.5 text-brand-cyan" /> Registered Channels
          </span>
          <div className="bg-[#090c10] border border-white/5 rounded-lg p-3 text-[11px] font-mono flex flex-col gap-2">
            {data.phones.length > 0 ? (
              data.phones.map((phone, idx) => (
                <div key={idx} className="flex justify-between items-center text-[#9eb1c2]">
                  <span>Mobile Line {idx + 1}:</span>
                  <span className="text-[#f1f3f5]">{phone}</span>
                </div>
              ))
            ) : (
              <span className="text-[#6b7c93] italic">No active phone links logged.</span>
            )}
          </div>
        </div>

        {/* Bank accounts */}
        <div className="flex flex-col gap-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-[#6b7c93] flex items-center gap-1.5">
            <CreditCard className="h-3.5 w-3.5 text-brand-yellow" /> Sourced Accounts
          </span>
          <div className="bg-[#090c10] border border-white/5 rounded-lg p-3 text-[11px] font-mono flex flex-col gap-2">
            {data.bank_accounts.length > 0 ? (
              data.bank_accounts.map((acct, idx) => (
                <div key={idx} className="flex justify-between items-center text-[#9eb1c2]">
                  <span>{acct.bank_name}:</span>
                  <span className="text-[#f1f3f5] text-[10px] truncate max-w-[150px]">{acct.account_number_hash}</span>
                </div>
              ))
            ) : (
              <span className="text-[#6b7c93] italic">No active banking records logged.</span>
            )}
          </div>
        </div>

        {/* Vehicles */}
        <div className="flex flex-col gap-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-[#6b7c93] flex items-center gap-1.5">
            <Car className="h-3.5 w-3.5 text-[#a855f7]" /> Tracked Vehicles
          </span>
          <div className="bg-[#090c10] border border-white/5 rounded-lg p-3 text-[11px] font-mono flex flex-col gap-2">
            {data.vehicles.length > 0 ? (
              data.vehicles.map((veh, idx) => (
                <div key={idx} className="flex justify-between items-center text-[#9eb1c2]">
                  <span>{veh.type}:</span>
                  <span className="text-[#f1f3f5] font-bold text-glow-yellow">{veh.registration_number}</span>
                </div>
              ))
            ) : (
              <span className="text-[#6b7c93] italic">No active vehicle logs.</span>
            )}
          </div>
        </div>
      </div>

      {/* Case History Timeline */}
      <div className="flex flex-col gap-3">
        <span className="text-[10px] font-mono uppercase tracking-wider text-[#6b7c93] flex items-center gap-1.5">
          <Calendar className="h-3.5 w-3.5 text-brand-red" /> Crime History Timeline ({data.history.length} cases)
        </span>
        
        <div className="relative border-l border-white/5 pl-4 ml-2 flex flex-col gap-4">
          {data.history.map((hist, idx) => (
            <div key={idx} className="relative text-xs">
              {/* Timeline marker */}
              <div className="absolute -left-[21px] top-1.5 h-2 w-2 rounded-full bg-brand-red border border-[#07090b]" />
              
              <div className="bg-white/2 border border-white/5 rounded-lg p-3 flex flex-col gap-1.5">
                <div className="flex justify-between items-start">
                  <span className="font-mono font-bold text-brand-cyan text-[11px]">{hist.fir_number}</span>
                  <span className="text-[9px] font-mono text-[#6b7c93]">{hist.date_filed}</span>
                </div>
                <div className="text-[11px] font-semibold text-[#f1f3f5] capitalize">
                  {hist.crime_type.replace('_', ' ')}
                </div>
                <div className="flex justify-between items-center text-[10px] font-mono text-[#9eb1c2] mt-1">
                  <span>Role: <span className="text-glow-yellow font-bold uppercase">{hist.role}</span></span>
                  <span className="px-1.5 py-0.5 rounded bg-white/5 text-[9px] uppercase">{hist.status}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
