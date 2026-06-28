'use client';

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for Leaflet default icon asset paths in React
// Even though we use CircleMarker, we keep this here for general safety
if (typeof window !== 'undefined') {
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  });
}

interface HotspotMapProps {
  data: {
    points: Array<{
      lat: number;
      lng: number;
      intensity: number;
      fir_number: string;
    }>;
  };
}

// Component to dynamically fit the bounds of the map to the data points
function ChangeView({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);

  return null;
}

export default function HotspotMap({ data }: HotspotMapProps) {
  // Determine map center based on average of points, or fallback to Bengaluru center
  const validPoints = data.points.filter(p => p.lat !== undefined && p.lng !== undefined && !isNaN(p.lat) && !isNaN(p.lng));
  
  const mapCenter: [number, number] = validPoints.length > 0
    ? [
        validPoints.reduce((acc, p) => acc + p.lat, 0) / validPoints.length,
        validPoints.reduce((acc, p) => acc + p.lng, 0) / validPoints.length
      ]
    : [12.9716, 77.5946]; // Bengaluru default

  const mapZoom = validPoints.length > 0 ? 11 : 9;

  return (
    <div className="glass-panel rounded-lg p-4 flex flex-col flex-1 border border-white/5 h-[450px] relative">
      <div className="p-2 border-b border-white/5 flex items-center justify-between mb-4">
        <span className="font-mono text-xs uppercase text-[#9eb1c2] tracking-wider">
          Crime Hotspot Density Map ({validPoints.length} points mapped)
        </span>
        <span className="text-[10px] font-mono text-[#6b7c93] uppercase">
          KSP Live Coordinates
        </span>
      </div>

      {/* Map Container */}
      <div className="flex-1 bg-[#090b0e] border border-white/5 rounded-lg overflow-hidden relative z-0">
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%' }}
        >
          <ChangeView center={mapCenter} zoom={mapZoom} />
          
          {/* CartoDB Dark Matter tile layer matches Stadium Noir UI */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            subdomains="abcd"
            maxZoom={20}
          />

          {validPoints.map((pt, idx) => (
            <CircleMarker
              key={idx}
              center={[pt.lat, pt.lng]}
              radius={12}
              fillColor="#ef4444"
              color="#ef4444"
              weight={1}
              opacity={0.8}
              fillOpacity={0.35}
            >
              <Popup className="leaflet-popup-dark">
                <div className="text-xs font-mono text-[#f1f3f5] bg-[#07090b] p-1.5 rounded border border-white/10">
                  <div className="font-bold text-glow-yellow border-b border-white/5 pb-1 mb-1 text-[10px]">
                    HOTSPOT INFO
                  </div>
                  <div><span className="text-[#6b7c93]">FIR Number:</span> {pt.fir_number}</div>
                  <div><span className="text-[#6b7c93]">Latitude:</span> {pt.lat.toFixed(5)}</div>
                  <div><span className="text-[#6b7c93]">Longitude:</span> {pt.lng.toFixed(5)}</div>
                  <div><span className="text-red-400">Intensity:</span> {(pt.intensity * 100).toFixed(0)}%</div>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      {/* Custom Legend */}
      <div className="absolute bottom-6 left-6 bg-[#07090b]/80 px-2 py-1.5 rounded border border-white/5 text-[8px] font-mono flex flex-col gap-1 text-[#9eb1c2] select-none pointer-events-none z-[1000]">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-red-500 inline-block opacity-80" /> 
          <span>High-Density Hotspot</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-red-500/20 border border-red-500 inline-block" /> 
          <span>Density Influence Zone</span>
        </div>
      </div>
    </div>
  );
}
