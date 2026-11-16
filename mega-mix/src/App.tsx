import { useState } from 'react'
import { Activity, Cpu, Terminal, Search, Microchip, Monitor, Boxes, Code2, ChevronRight, CircleDot, Github, Menu, Command, Radio, ShieldCheck, Zap } from 'lucide-react'

type ModuleId = 'overview' | 'gnu' | 'pico' | 'qemu' | 'studio'
const modules: { id: ModuleId; title: string; subtitle: string; icon: typeof Terminal; color: string }[] = [
  { id: 'gnu', title: 'GNU Workbench', subtitle: 'Search · shell · diagnostics', icon: Terminal, color: 'green' },
  { id: 'pico', title: 'Pico Lab', subtitle: 'RP2040 · RP2350 · firmware', icon: Microchip, color: 'cyan' },
  { id: 'qemu', title: 'QEMU Engine', subtitle: 'Virtual machines · CPU emulation', icon: Monitor, color: 'purple' },
  { id: 'studio', title: 'Vite Studio', subtitle: 'React · TypeScript · live preview', icon: Code2, color: 'orange' },
]
const descriptions: Record<ModuleId, string> = {
  overview: 'A unified workspace for source retrieval, embedded development and virtual machine labs.',
  gnu: 'GNU-compatible search workflows, syntax-aware results and project diagnostics.',
  pico: 'Build firmware for physical Raspberry Pi Pico-family boards with the official Pico SDK.',
  qemu: 'Manage QEMU system-emulation profiles and launch guest operating systems on supported hosts.',
  studio: 'Develop the MEGA MIX interface with Vite, React and TypeScript.',
}
const commands: Record<ModuleId, string[]> = {
  overview: ['npm run dev', 'npm run build', 'npm run typecheck'],
  gnu: ['grep -Rni --exclude-dir=node_modules "pattern" .', 'git diff --check', 'python -m unittest discover -s tests -v'],
  pico: ['cmake -S pico -B build/pico -DPICO_BOARD=pico', 'cmake --build build/pico', 'picotool info build/pico/firmware.uf2'],
  qemu: ['qemu-system-x86_64 --version', 'qemu-img create -f qcow2 disk.qcow2 16G', './scripts/qemu-launch.sh disk.qcow2'],
  studio: ['npm install', 'npm run dev', 'npm run build'],
}
function App() {
  const [active, setActive] = useState<ModuleId>('overview')
  const [query, setQuery] = useState('')
  const [mobileOpen, setMobileOpen] = useState(false)
  const selected = modules.find(m => m.id === active)
  const filtered = modules.filter(m => (m.title + m.subtitle).toLowerCase().includes(query.toLowerCase()))
  return <div className="shell">
    <aside className={mobileOpen ? 'sidebar open' : 'sidebar'}>
      <div className="brand"><div className="brand-mark"><Boxes size={21}/></div><div><b>GREP <span>MEGA MIX</span></b><small>DEVELOPER ENVIRONMENT</small></div></div>
      <div className="workspace-label">WORKSPACE</div>
      <button className={active === 'overview' ? 'nav active' : 'nav'} onClick={() => {setActive('overview');setMobileOpen(false)}}><Activity size={17}/> Command Center</button>
      <div className="workspace-label">TOOLCHAINS</div>
      {modules.map(m => <button key={m.id} className={active === m.id ? 'nav active' : 'nav'} onClick={() => {setActive(m.id);setMobileOpen(false)}}><m.icon size={17}/>{m.title}<ChevronRight className="nav-arrow" size={14}/></button>)}
      <div className="sidebar-bottom"><div className="status-line"><span className="pulse"/> LOCAL WORKSPACE</div><small>Standalone profile · v0.1.0</small></div>
    </aside>
    <main className="main">
      <header className="topbar"><button className="icon-btn mobile-menu" onClick={() => setMobileOpen(!mobileOpen)}><Menu size={19}/></button><div className="crumb">GREP <span>/</span> MEGA MIX <span>/</span> {active.toUpperCase()}</div><div className="top-actions"><span className="host-pill"><CircleDot size={12}/> CODESPACES READY</span><a className="icon-btn" href="https://github.com/checksystemsadmin/grep-language" target="_blank" rel="noreferrer" aria-label="GitHub repository"><Github size={18}/></a></div></header>
      <section className="content">
        <div className="hero"><div><div className="eyebrow"><Zap size={13}/> INTEGRATED ENGINEERING WORKSPACE</div><h1>{active === 'overview' ? <>Build beyond<br/><em>the terminal.</em></> : selected?.title}</h1><p>{descriptions[active]}</p><div className="hero-tags"><span>GNU CORE</span><span>RASPBERRY PI PICO</span><span>QEMU TCG</span><span>VITE + REACT</span></div></div><div className="hero-art"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="core-chip"><Cpu size={48}/><b>GMX</b></div><div className="orbit-node node-a"><Terminal size={17}/></div><div className="orbit-node node-b"><Microchip size={17}/></div><div className="orbit-node node-c"><Monitor size={17}/></div></div></div>
        <div className="section-head"><div><div className="eyebrow">SYSTEM MODULES</div><h2>Engineering suite</h2></div><div className="searchbox"><Search size={15}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Filter modules"/></div></div>
        <div className="module-grid">{filtered.map(m => <button className="module-card" key={m.id} onClick={() => setActive(m.id)}><div className={'module-icon '+m.color}><m.icon size={21}/></div><div className="card-title">{m.title}<ChevronRight size={16}/></div><p>{m.subtitle}</p><div className="card-footer"><span><span className="tiny-dot"/> MODULE PROFILE</span><span>OPEN <ChevronRight size={12}/></span></div></button>)}</div>
        <div className="lower-grid"><section className="panel"><div className="panel-head"><div><div className="eyebrow">QUICK ACTIONS</div><h3>{active === 'overview' ? 'Workspace commands' : selected?.title + ' commands'}</h3></div><Command size={18}/></div><div className="command-list">{commands[active].map((cmd,i)=><div className="command" key={cmd}><span>{String(i+1).padStart(2,'0')}</span><code>{cmd}</code><button title="Copy command" onClick={() => navigator.clipboard?.writeText(cmd)}>COPY</button></div>)}</div><p className="hint">Commands are reference actions; this browser UI does not execute host shell commands.</p></section>
        <section className="panel health"><div className="panel-head"><div><div className="eyebrow">ENVIRONMENT</div><h3>Integration status</h3></div><Activity size={18}/></div><div className="health-row"><span><Terminal size={16}/> GNU toolchain</span><b className="planned">HOST CHECK REQUIRED</b></div><div className="health-row"><span><Microchip size={16}/> Pico SDK</span><b className="planned">OPTIONAL</b></div><div className="health-row"><span><Monitor size={16}/> QEMU</span><b className="planned">OPTIONAL</b></div><div className="health-row"><span><Radio size={16}/> Hardware link</span><b className="planned">NOT CONNECTED</b></div><div className="security-note"><ShieldCheck size={16}/><span>Project-local setup. No global installs or automatic host execution.</span></div></section></div>
        <footer><span>GREP MEGA MIX <b>0.1.0</b></span><span>BUILT FOR OPEN ENGINEERING <span className="footer-dot">●</span></span></footer>
      </section>
    </main>
  </div>
}
export default App