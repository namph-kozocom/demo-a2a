'use client';

import { Download, ChevronDown, Check, User } from 'lucide-react';
import styles from './Header.module.css';
import { useState } from 'react';

interface HeaderProps {
  activeTab: 'preview' | 'code';
  onTabChange: (tab: 'preview' | 'code') => void;
}

export default function Header({ activeTab, onTabChange }: HeaderProps) {
  return (
    <header className={styles.header}>
      {/* Left: App Name */}
      <div className={styles.appName}>
        <span>A2A Web Builder</span>
        <ChevronDown size={16} />
      </div>

      {/* Center: Tab Buttons */}
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'preview' ? styles.active : ''}`}
          onClick={() => onTabChange('preview')}
        >
          Preview
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'code' ? styles.active : ''}`}
          onClick={() => onTabChange('code')}
        >
          Code
        </button>
      </div>

      {/* Right: Action Buttons */}
      <div className={styles.actions}>
        <button className={styles.downloadBtn}>
          <Download size={16} />
          <span>Zip</span>
        </button>
        <button className={styles.actionBtn}>
          Integrations
        </button>
        <button className={styles.actionBtn}>
          <Check size={16} />
          <span>Deployed</span>
        </button>
        <div className={styles.avatar}>
          <User size={16} />
        </div>
      </div>
    </header>
  );
}
