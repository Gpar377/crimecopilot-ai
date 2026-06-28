'use client';

import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';

interface NetworkGraphProps {
  data: {
    nodes: any[];
    edges: any[];
  };
  onNodeClick?: (id: string, type: string, label: string) => void;
}

export default function NetworkGraph({ data, onNodeClick }: NetworkGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Destroy previous instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Format elements for cytoscape
    const elements = [
      ...data.nodes.map(n => ({
        group: 'nodes' as const,
        data: {
          id: n.data.id,
          label: n.data.label,
          type: n.data.type,
          ...n.data
        }
      })),
      ...data.edges.map(e => ({
        group: 'edges' as const,
        data: {
          id: e.data.id,
          source: e.data.source,
          target: e.data.target,
          label: e.data.label
        }
      }))
    ];

    // Colors per node type matching the Stadium Noir theme
    const getNodeColor = (type: string) => {
      switch (type) {
        case 'Accused':
          return '#ef4444'; // Red
        case 'FIR':
          return '#3b82f6'; // Blue
        case 'Location':
        case 'PoliceStation':
          return '#10b981'; // Emerald
        case 'Vehicle':
          return '#eab308'; // Amber/Gold
        case 'Phone':
          return '#06b6d4'; // Cyan
        case 'BankAccount':
          return '#8b5cf6'; // Violet
        default:
          return '#9ca3af'; // Gray
      }
    };

    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (ele: any) => getNodeColor(ele.data('type')),
            'label': 'data(label)',
            'color': '#f3f4f6',
            'font-size': '10px',
            'font-family': 'monospace',
            'text-valign': 'bottom',
            'text-margin-y': 4,
            'width': '22px',
            'height': '22px',
            'overlay-opacity': 0,
            'transition-property': 'background-color, line-color, target-arrow-color',
            'transition-duration': 0.3
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': '2px',
            'border-color': '#ffffff',
            'background-color': '#ffffff',
            'width': '26px',
            'height': '26px'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': 'rgba(255, 255, 255, 0.15)',
            'target-arrow-color': 'rgba(255, 255, 255, 0.15)',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '8px',
            'font-family': 'monospace',
            'color': '#9ca3af',
            'text-background-opacity': 0.8,
            'text-background-color': '#07090b',
            'text-background-padding': '2px',
            'text-background-shape': 'roundrectangle',
            'text-margin-y': -10
          }
        },
        {
          selector: 'edge:selected',
          style: {
            'width': 2.5,
            'line-color': '#06b6d4',
            'target-arrow-color': '#06b6d4',
            'color': '#06b6d4'
          }
        }
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 500,
        fit: true,
        padding: 40,
        nodeOverlap: 20,
        componentSpacing: 40,
        refresh: 20,
        idealEdgeLength: (edge: any) => 80,
        edgeElasticity: (edge: any) => 100,
        nodeRepulsion: (node: any) => 4000
      }
    });

    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const nodeData = node.data();
      setSelectedNode(nodeData);
      if (onNodeClick) {
        onNodeClick(nodeData.id, nodeData.type, nodeData.label);
      }
    });

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedNode(null);
      }
    });

    cyRef.current = cy;

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [data]);

  const triggerLayout = (layoutName: string) => {
    if (!cyRef.current) return;
    const layout = cyRef.current.layout({
      name: layoutName,
      animate: true,
      fit: true,
      padding: 30
    } as any);
    layout.run();
  };

  return (
    <div className="glass-panel rounded-lg p-4 flex flex-col flex-1 border border-white/5 h-[450px] relative">
      <div className="p-2 border-b border-white/5 flex items-center justify-between mb-4">
        <span className="font-mono text-xs uppercase text-[#9eb1c2] tracking-wider">
          Criminal Network Graph ({data.nodes.length} nodes)
        </span>
        <div className="flex gap-1.5">
          <button 
            type="button"
            onClick={() => triggerLayout('cose')}
            className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[9px] font-mono text-[#9eb1c2] hover:bg-white/10 transition-all cursor-pointer"
          >
            Force
          </button>
          <button 
            type="button"
            onClick={() => triggerLayout('concentric')}
            className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[9px] font-mono text-[#9eb1c2] hover:bg-white/10 transition-all cursor-pointer"
          >
            Circle
          </button>
          <button 
            type="button"
            onClick={() => triggerLayout('grid')}
            className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[9px] font-mono text-[#9eb1c2] hover:bg-white/10 transition-all cursor-pointer"
          >
            Grid
          </button>
        </div>
      </div>

      {/* Canvas */}
      <div ref={containerRef} className="flex-1 bg-[#090b0e] border border-white/5 rounded-lg overflow-hidden relative" />

      {/* Detail Overlay */}
      {selectedNode && (
        <div className="absolute bottom-6 left-6 right-6 bg-[#07090b]/95 border border-white/10 rounded-lg p-3 backdrop-blur-md text-[11px] font-mono shadow-2xl flex flex-col gap-1 transition-all z-10">
          <div className="flex justify-between items-center border-b border-white/5 pb-1">
            <span className="text-glow-cyan uppercase text-[10px] tracking-wider font-bold">Node Properties</span>
            <button 
              type="button"
              onClick={() => setSelectedNode(null)}
              className="text-[#6b7c93] hover:text-[#f1f3f5]"
            >
              ×
            </button>
          </div>
          <div><span className="text-[#6b7c93]">ID:</span> {selectedNode.id}</div>
          <div><span className="text-[#6b7c93]">Label:</span> {selectedNode.label}</div>
          <div><span className="text-[#6b7c93]">Type:</span> {selectedNode.type}</div>
          {selectedNode.risk_score !== undefined && (
            <div><span className="text-[#ef4444]">Risk Score:</span> {selectedNode.risk_score}/100</div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="absolute top-20 left-6 bg-[#07090b]/80 px-2 py-1.5 rounded border border-white/5 text-[8px] font-mono flex flex-col gap-1 text-[#9eb1c2] select-none pointer-events-none z-10">
        <div className="flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-red-500 inline-block" /> Accused</div>
        <div className="flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-blue-500 inline-block" /> FIR Case</div>
        <div className="flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-emerald-500 inline-block" /> Location</div>
        <div className="flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-cyan-400 inline-block" /> Phone</div>
        <div className="flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-violet-500 inline-block" /> Bank Account</div>
      </div>
    </div>
  );
}
