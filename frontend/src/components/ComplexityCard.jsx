import React from 'react';
import { Clock, HardDrive, ArrowRight, Zap } from 'lucide-react';

export default function ComplexityCard({ complexity }) {
  if (!complexity) return null;

  const userTime = complexity.userTime || complexity.user_time || 'O(N)';
  const optimalTime = complexity.optimalTime || complexity.optimal_time || 'O(N)';
  const userSpace = complexity.userSpace || complexity.user_space || 'O(1)';
  const optimalSpace = complexity.optimalSpace || complexity.optimal_space || 'O(1)';

  const isTimeOptimal = userTime.replace(/\s+/g, '') === optimalTime.replace(/\s+/g, '');

  return (
    <div className="complexity-grid">
      {/* Time Complexity */}
      <div className="complexity-card">
        <div className="complexity-title">
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Clock size={14} style={{ color: 'var(--accent-cyan)' }} />
            <span>Time Complexity</span>
          </div>
          {isTimeOptimal ? (
            <span style={{ fontSize: '0.65rem', color: 'var(--accent-emerald)', fontWeight: 700 }}>OPTIMAL</span>
          ) : (
            <span style={{ fontSize: '0.65rem', color: 'var(--accent-amber)', fontWeight: 700 }}>SUBOPTIMAL</span>
          )}
        </div>
        <div className="complexity-value" style={{ color: isTimeOptimal ? '#34d399' : '#fbbf24' }}>
          {userTime}
        </div>
        <div className="complexity-target">
          <ArrowRight size={12} />
          <span>Optimal Target: <strong>{optimalTime}</strong></span>
        </div>
      </div>

      {/* Space Complexity */}
      <div className="complexity-card">
        <div className="complexity-title">
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <HardDrive size={14} style={{ color: 'var(--accent-secondary)' }} />
            <span>Space Complexity</span>
          </div>
          <span style={{ fontSize: '0.65rem', color: 'var(--text-dim)', fontWeight: 700 }}>AUXILIARY</span>
        </div>
        <div className="complexity-value" style={{ color: '#c084fc' }}>
          {userSpace}
        </div>
        <div className="complexity-target" style={{ color: 'var(--text-muted)' }}>
          <ArrowRight size={12} />
          <span>Optimal Target: <strong>{optimalSpace}</strong></span>
        </div>
      </div>
    </div>
  );
}
