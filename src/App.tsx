/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { 
  Terminal, 
  Cpu, 
  Code2, 
  FileJson, 
  ChevronRight, 
  Play, 
  CheckCircle2, 
  AlertCircle,
  Database,
  Layers,
  Settings,
  ShieldCheck,
  Search,
  Hash
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

const MOCK_BUFFER = [
  "                                Order Entry - Main                              ",
  " Order # 12345678                                                               ",
  "                                                                                ",
  " Customer ID: CUST001                                                           ",
  "                                                                                ",
  " Items:                                                                         ",
  "   1. Widget A                                                                  ",
  "   2. Widget B                                                                  ",
  "                                                                                ",
  "                                                                                ",
  "                                                                                ",
  "                                                                                ",
  "                                                                                ",
  "                                                                                ",
  "                                                                                ",
  "                                                                                ",
  "                                                                                ",
  "                                                                                ",
  "                                                                                ",
  "                                                  Total:      1234.56           ",
  "                                                                                ",
  "                                                                                ",
  "                                                                                ",
  " System Ready                                                                   "
];

const YAML_EXAMPLE = `order_entry_main:
  screen_name: "Order Entry - Main"
  
  indicators:
    - "Order Entry"
    - text: "Order #"
      row: 1
      col: 5
    - text: "System Ready"
      row: 24
      col: 1
  
  handlers:
    - name: "find_error"
      type: "text_block_search"
      search_term: "ERROR"
      start_row: 1
      end_row: 10
      required: false
    
    - name: "extract_total"
      type: "extract_number"
      row: 20
      col: 50
      length: 10
      decimal_places: 2
      required: true`;

export default function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'terminal' | 'code' | 'yaml'>('overview');
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<any>(null);

  const runVerification = () => {
    setIsVerifying(true);
    setVerificationResult(null);
    setTimeout(() => {
      setIsVerifying(false);
      setVerificationResult({
        success: true,
        handlers: {
          find_error: { found: false, search_term: "ERROR" },
          extract_total: { value: 1234.56, formatted: "1234.56", success: true }
        }
      });
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-gray-300 selection:bg-green-500/30">
      {/* Sidebar */}
      <div className="fixed left-0 top-0 bottom-0 w-64 bg-[#111111] border-r border-white/5 flex flex-col">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-8 h-8 rounded bg-green-500/10 flex items-center justify-center border border-green-500/20">
              <Terminal className="w-5 h-5 text-green-500" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white italic">SGCIronConnect</h1>
          </div>

          <nav className="space-y-1">
            <NavItem 
              active={activeTab === 'overview'} 
              onClick={() => setActiveTab('overview')} 
              icon={<Layers className="w-4 h-4" />}
              label="Architecture" 
            />
            <NavItem 
              active={activeTab === 'terminal'} 
              onClick={() => setActiveTab('terminal')} 
              icon={<Terminal className="w-4 h-4" />}
              label="Live Emulator" 
            />
            <NavItem 
              active={activeTab === 'code'} 
              onClick={() => setActiveTab('code')} 
              icon={<Code2 className="w-4 h-4" />}
              label="Python Framework" 
            />
            <NavItem 
              active={activeTab === 'yaml'} 
              onClick={() => setActiveTab('yaml')} 
              icon={<FileJson className="w-4 h-4" />}
              label="Scaling Strategy" 
            />
          </nav>
        </div>

        <div className="mt-auto p-6 space-y-4">
          <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/10 active:scale-95 transition-transform cursor-pointer" onClick={runVerification}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase tracking-widest text-blue-500 font-bold">LPAR Status</span>
              <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
            </div>
            <p className="text-xs text-gray-400">SafeGuaranteed verification session active.</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="ml-64 p-12 max-w-6xl">
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && <Overview key="overview" />}
          {activeTab === 'terminal' && (
            <TerminalEmulator 
              key="terminal" 
              isVerifying={isVerifying} 
              verificationResult={verificationResult} 
              onVerify={runVerification} 
            />
          )}
          {activeTab === 'code' && <CodeViewer key="code" />}
          {activeTab === 'yaml' && <ScalingViewer key="yaml" />}
        </AnimatePresence>
      </main>
    </div>
  );
}

function NavItem({ active, onClick, icon, label }: { active: boolean, onClick: () => void, icon: React.ReactNode, label: string }) {
  return (
    <button 
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
        active 
          ? 'bg-white/5 text-white' 
          : 'text-gray-500 hover:text-gray-300 hover:bg-white/2'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function Overview() {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      exit={{ opacity: 0, y: -20 }}
      className="space-y-12"
    >
      <header className="space-y-4">
        <h2 className="text-4xl font-light text-white tracking-tight">SafeGuarded Copy <span className="text-blue-400 italic">Validation</span></h2>
        <p className="text-lg text-gray-400 max-w-2xl leading-relaxed">
          SGCIronConnect is an enterprise-grade automation framework for IBM i terminal sessions, 
          specifically optimized for verifying system integrity after <strong>IBM FlashSystem SafeGuarded Copy</strong> snapshot restores.
        </p>
      </header>

      <div className="grid grid-cols-3 gap-6">
        <FeatureCard 
          icon={<ShieldCheck className="w-5 h-5 text-blue-400" />}
          title="Rapid Validation"
          description="Automate 5250 login and status verification on cloned LPARs in seconds, reducing RTO for snapshot testing."
        />
        <FeatureCard 
          icon={<Search className="w-5 h-5 text-blue-400" />}
          title="Data-Driven Handlers"
          description="No Python code required for new screens. Simply define indicators and extraction handlers in YAML."
        />
        <FeatureCard 
          icon={<Hash className="w-5 h-5 text-blue-400" />}
          title="Snapshot Guard"
          description="Verify subsystem availability, storage utilization, and TCP/IP stack health post-restore automatically."
        />
      </div>

      <div className="space-y-6">
        <h3 className="text-xs uppercase tracking-[0.2em] text-gray-500 font-bold">The Architecture</h3>
        <div className="relative p-8 rounded-2xl bg-white/2 border border-white/5 backdrop-blur-3xl">
          <div className="flex flex-col gap-4">
            <ArchLayer level={4} title="Orchestration" desc="Robot Framework Library (IBMiLibrary)" />
            <ArchLayer level={3} title="Generic Verification" desc="BaseScreen: 1 Class handles 100+ screens" />
            <ArchLayer level={2} title="Snapshot Intelligence" desc="Regional Buffer Handlers for Numeric Data" />
            <ArchLayer level={1} title="Terminal Driver" desc="TmuxDriver & libtmux session control" />
            <ArchLayer level={0} title="Emulator" desc="tn5250 binary (Map: 285)" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="p-6 rounded-2xl bg-white/2 border border-white/5 hover:border-white/10 transition-colors group">
      <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <h4 className="text-white font-medium mb-2">{title}</h4>
      <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
    </div>
  );
}

function ArchLayer({ level, title, desc }: { level: number, title: string, desc: string }) {
  return (
    <div className="flex items-center gap-6 group">
      <div className="w-12 text-xs font-mono text-gray-600">L0{level}</div>
      <div className="flex-1 p-4 rounded-xl border border-white/5 bg-white/[0.01] group-hover:bg-white/[0.03] transition-colors flex items-center justify-between">
        <span className="text-sm font-medium text-gray-300">{title}</span>
        <span className="text-xs text-gray-500 italic">{desc}</span>
      </div>
    </div>
  );
}

function TerminalEmulator({ isVerifying, verificationResult, onVerify }: any) {
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }} 
      animate={{ opacity: 1, scale: 1 }} 
      exit={{ opacity: 0, scale: 0.98 }}
      className="space-y-8"
    >
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-medium text-white">Verification <span className="text-blue-400">Terminal</span></h2>
          <p className="text-sm text-gray-500 leading-relaxed">Simulated 5250 session verifying a SafeGuarded Copy snapshot.</p>
        </div>
        <button 
          onClick={onVerify}
          disabled={isVerifying}
          className="flex items-center gap-2 px-6 py-2.5 bg-blue-500 text-white font-bold text-sm rounded-lg hover:bg-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
        >
          {isVerifying ? <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
          START VALIDATION
        </button>
      </div>

      <div className="grid grid-cols-12 gap-8">
        <div className="col-span-8 relative">
          <div className="p-1 rounded-xl bg-gray-900 border border-gray-800 shadow-2xl relative overflow-hidden">
            <div className="absolute inset-0 terminal-scanline opacity-20" />
            <div className="p-8 font-mono text-[13px] leading-none whitespace-pre bg-black/80 rounded-lg overflow-x-auto text-blue-300 terminal-glow custom-scrollbar">
              {MOCK_BUFFER.map((line, i) => (
                <div key={i} className="hover:bg-blue-500/5 px-2 -mx-2">{line}</div>
              ))}
            </div>
          </div>
          <div className="mt-4 flex items-center gap-4 text-[10px] uppercase tracking-widest text-gray-600 font-mono">
            <span>READY</span>
            <div className="w-1 h-1 rounded-full bg-gray-600" />
            <span>LPAR CLONE 07</span>
            <div className="w-1 h-1 rounded-full bg-gray-600" />
            <span>SGC SNAPSHOT CHECK</span>
          </div>
        </div>

        <div className="col-span-4 space-y-6">
          <div className="p-6 rounded-2xl border border-white/5 bg-white/2 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-widest text-gray-500">Node Analysis</h3>
            <div className="space-y-3">
              <HandlerStatus 
                name="SGC_ID_VERIFY" 
                type="Match" 
                status={verificationResult ? 'success' : isVerifying ? 'loading' : 'idle'}
                detail={verificationResult ? "Verified" : "Pending"}
              />
              <HandlerStatus 
                name="EXTRACT_TOTAL" 
                type="Metrics" 
                status={verificationResult ? 'success' : isVerifying ? 'loading' : 'idle'}
                detail={verificationResult ? `1234.56` : "Scanning"}
              />
            </div>
          </div>

          <div className="p-6 rounded-2xl border border-white/5 bg-white/2 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-widest text-gray-500">Session Config</h3>
            <div className="space-y-2 font-mono text-[10px]">
              <div className="flex justify-between border-b border-white/5 pb-1">
                <span className="text-gray-500">Transport:</span>
                <span className="text-blue-400">tn5250 bin (mux)</span>
              </div>
              <div className="flex justify-between border-b border-white/5 pb-1">
                <span className="text-gray-500">Map:</span>
                <span className="text-blue-400">285</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">SSL:</span>
                <span className="text-green-500">ENABLED</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function HandlerStatus({ name, type, status, detail }: { name: string, type: string, status: 'idle' | 'loading' | 'success', detail: string }) {
  return (
    <div className="flex items-center justify-between group">
      <div className="flex items-center gap-3">
        <div className={`w-1.5 h-1.5 rounded-full ${
          status === 'success' ? 'bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.5)]' : 
          status === 'loading' ? 'bg-yellow-500 animate-pulse' : 'bg-gray-700'
        }`} />
        <div>
          <div className="text-[11px] font-bold text-gray-300 flex items-center gap-2">
            {name}
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/10 text-gray-500 font-normal">{type}</span>
          </div>
          <div className="text-[10px] text-gray-500 font-mono mt-1">{detail}</div>
        </div>
      </div>
      {status === 'success' && <CheckCircle2 className="w-4 h-4 text-blue-400" />}
    </div>
  );
}

function CodeViewer() {
  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }} 
      animate={{ opacity: 1, x: 0 }} 
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-2xl text-white font-medium">Generic <span className="text-blue-400">BaseScreen</span> Logic</h2>
        <div className="flex items-center gap-4 text-xs font-mono text-gray-500">
          <span>PEP8 Compliant</span>
          <span>Scalable</span>
        </div>
      </div>

      <div className="rounded-2xl overflow-hidden border border-white/5 bg-[#111111]">
        <div className="flex items-center px-4 py-3 bg-white/2 border-b border-white/5 gap-2">
          <Terminal className="w-3.5 h-3.5 text-blue-400" />
          <span className="text-xs font-mono text-gray-400">framework/core/base_screen.py</span>
        </div>
        <pre className="p-6 overflow-x-auto text-sm font-mono text-blue-200 custom-scrollbar leading-relaxed">
{`class BaseScreen:
    """One class to rule them all (screens)."""
    def __init__(self, driver, yaml_path, screen_key):
        self.driver = driver
        # Loads ANY screen definition from ANY yaml file
        self.config = load_yaml(yaml_path).get(screen_key)
        self.indicators = self.config.get('indicators', [])

    def verify(self):
        """Standardized verification logic for 100+ screens."""
        buffer = self.driver.get_buffer()
        for ind in self.indicators:
            self._check_indicator(ind, buffer)`}
        </pre>
      </div>
    </motion.div>
  );
}

function ScalingViewer() {
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }} 
      animate={{ opacity: 1, scale: 1 }} 
      exit={{ opacity: 0, scale: 0.95 }}
      className="space-y-6"
    >
      <div className="space-y-2">
        <h2 className="text-2xl text-white font-medium">Workflow <span className="text-blue-400">Navigation</span></h2>
        <p className="text-sm text-gray-400 leading-relaxed">Chaining screens through verification and control key sequences.</p>
      </div>

      <div className="grid grid-cols-2 gap-8">
        <div className="p-8 rounded-2xl bg-white/2 border border-white/5 flex flex-col gap-6">
          <div className="space-y-2">
            <h4 className="text-white font-semibold">Granular Control Keys</h4>
            <p className="text-xs text-gray-500 leading-relaxed">
              Navigation is handled by the <code className="text-blue-400">Press Key</code> keyword. 
              This sends terminal signals for Enter, F3, PgUp, and even specialized IBM i keys like FieldExit.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {['Enter', 'F3', 'F12', 'PgUp', 'PgDn', 'FieldExit'].map(k => (
              <div key={k} className="px-3 py-2 rounded bg-black/40 border border-white/5 text-[10px] text-blue-300 font-mono text-center">
                {k}
              </div>
            ))}
          </div>
        </div>

        <div className="p-8 rounded-2xl bg-white/2 border border-white/5 flex flex-col justify-center gap-6">
          <div className="space-y-2">
            <h4 className="text-white font-semibold">Chained Verification Workflow</h4>
            <p className="text-xs text-gray-500 leading-relaxed">
              Verifying 30+ screens is simply a matter of checking state, interacting, and moving to the next.
            </p>
          </div>
          <div className="p-4 rounded-lg bg-black/40 font-mono text-[9px] text-green-400 border border-white/5 leading-relaxed">
            # Full Snapshot Restoration Test<br/>
            Verify Screen&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;login<br/>
            Type Text&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user&nbsp;&nbsp;QSECOFR<br/>
            Press Key&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enter<br/>
            <br/>
            # Handle optional IBM i info screen<br/>
            Handle Optional Signon Info<br/>
            <br/>
            Verify Screen&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;main_menu<br/>
            Type Text&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cmd&nbsp;&nbsp;'WRKSYSSTS'<br/>
            Press Key&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enter<br/>
            <br/>
            Verify Screen&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sys_status_check
          </div>
        </div>
      </div>
    </motion.div>
  );
}
