import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  LayoutDashboard, 
  AlertCircle, 
  Users,
  CheckCircle2, 
  Settings, 
  LogOut,
  Droplets,
  Zap,
  Trash2,
  TrendingUp,
  Award,
  Filter,
  BarChart3,
  Search,
  Bell,
  ChevronRight,
  ShieldCheck,
  User,
  Map,
  Shield,
  Clock,
  CheckCircle,
  AlertTriangle,
  HelpCircle,
  MessageCircle
} from 'lucide-react';
import { 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  AreaChart,
  Area,
  CartesianGrid
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'https://eco-track-c7zf.onrender.com/api';

// Staff Data with Multi-tier Roles
const STAFF_LIST = [
  { id: 'elec_staff', name: 'Electrical Staff', role: 'Staff', dept: 'Electricity', icon: Zap },
  { id: 'elec_head', name: 'Electrical Head', role: 'Head', dept: 'Electricity', icon: Zap },
  { id: 'water_staff', name: 'Water Staff', role: 'Staff', dept: 'Water', icon: Droplets },
  { id: 'water_head', name: 'Water Head', role: 'Head', dept: 'Water', icon: Droplets },
  { id: 'sewage_staff', name: 'Waste Staff', role: 'Staff', dept: 'Sewage', icon: Trash2 },
  { id: 'sewage_head', name: 'Waste Head', role: 'Head', dept: 'Sewage', icon: Trash2 },
];

const App = () => {
  const [currentUser, setCurrentUser] = useState({ id: 'admin', name: 'Global Admin', role: 'admin', dept: null });
  const [showRolePicker, setShowRolePicker] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedDept, setSelectedDept] = useState(null);
  const [selectedStatus, setSelectedStatus] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [stats, setStats] = useState(null);
  const [reports, setReports] = useState([]);
  const [nudges, setNudges] = useState([]);
  const [supportRequests, setSupportRequests] = useState([]);
  const [supportTab, setSupportTab] = useState('active');
  const [notification, setNotification] = useState(null);
  const [loading, setLoading] = useState(true);
  const [areas, setAreas] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [selectedAreaId, setSelectedAreaId] = useState(null);
  const [areaStats, setAreaStats] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);

  // Sync selectedDept with current user's department
  useEffect(() => {
    if (currentUser.role === 'admin') {
      setSelectedDept(null);
    } else {
      setSelectedDept(currentUser.dept);
    }
  }, [currentUser]);

  const fetchData = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      const deptToFilter = currentUser.role === 'admin' ? selectedDept : currentUser.dept;
      
      if (deptToFilter) params.append('dept', deptToFilter.toLowerCase());
      if (selectedStatus) params.append('status', selectedStatus);
      if (activeTab === 'delayed') params.append('delayed', 'true');
      if (searchQuery) params.append('search', searchQuery);
      
      const [overviewRes, reportsRes, areasRes, nudgesRes, supportRes] = await Promise.all([
        axios.get(`${API_BASE}/overview`),
        axios.get(`${API_BASE}/reports`, { params }),
        axios.get(`${API_BASE}/areas`),
        currentUser.dept ? axios.get(`${API_BASE}/nudges`, { params: { dept: currentUser.dept.toLowerCase() } }) : Promise.resolve({ data: [] }),
        currentUser.role === 'admin' ? axios.get(`${API_BASE}/support`) : Promise.resolve({ data: [] })
      ]);
      setStats(overviewRes.data);
      setReports(reportsRes.data);
      setAreas(areasRes.data);
      setNudges(nudgesRes.data);
      setSupportRequests(supportRes.data || []);
      if (!selectedAreaId && areasRes.data.length > 0) setSelectedAreaId(areasRes.data[0].area_id);
      setLoading(false);
    } catch (err) {
      console.error("Fetch error:", err);
    }
  }, [selectedDept, selectedStatus, currentUser, selectedAreaId, activeTab, searchQuery]);

  const fetchAreaStats = useCallback(async () => {
    if (!selectedAreaId) return;
    try {
      const [statsRes, hotspotsRes] = await Promise.all([
        axios.get(`${API_BASE}/areas/${selectedAreaId}/stats`),
        axios.get(`${API_BASE}/areas/${selectedAreaId}/hotspots`)
      ]);
      setAreaStats(statsRes.data);
      setHotspots(hotspotsRes.data);
    } catch (err) {
      console.error("Area details fetch error:", err);
    }
  }, [selectedAreaId]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

  useEffect(() => {
    fetchAreaStats();
  }, [fetchAreaStats]);

  const handleIdentityChange = (newIdentity) => {
    console.log("Switching identity to:", newIdentity.name);
    setCurrentUser(newIdentity);
    setShowRolePicker(false);
  };

  const handleResolve = async (reportId) => {
    try {
      await axios.post(`${API_BASE}/reports/${reportId}/resolve`, {
        staff_id: currentUser.id
      });
      fetchData();
    } catch (err) {
      console.error("Resolve error:", err);
      alert("Failed to resolve report. Please try again.");
    }
  };

  const handleNudge = async (reportId) => {
    try {
      await axios.post(`${API_BASE}/nudges`, {
        report_id: reportId,
        dept_id: currentUser.dept.toLowerCase(),
        sender_id: currentUser.id,
        message: `Head Alert: Please prioritize this ticket immediately.`
      });
      setNotification({ type: 'success', message: `Alert successfully sent to staff for ${reportId}` });
      setTimeout(() => setNotification(null), 4000);
      fetchData();
    } catch (err) {
      console.error("Nudge error:", err);
      setNotification({ type: 'error', message: 'Failed to send alert. Please try again.' });
      setTimeout(() => setNotification(null), 4000);
    }
  };

  const handleResolveSupport = async (reqId) => {
    try {
      await axios.post(`${API_BASE}/support/${reqId}/resolve`);
      setNotification({ type: 'success', message: 'Message marked as resolved.' });
      setTimeout(() => setNotification(null), 3000);
      fetchData();
    } catch (err) {
      console.error("Resolve support error:", err);
      setNotification({ type: 'error', message: 'Failed to resolve message.' });
      setTimeout(() => setNotification(null), 3000);
    }
  };

  useEffect(() => {
    if (currentUser.role !== 'admin') {
      const interval = setInterval(fetchData, 10000); // Poll every 10s for staff/head
      return () => clearInterval(interval);
    }
  }, [currentUser, fetchData]);

  const SidebarItem = ({ id, icon: Icon, label, badge }) => (
    <button 
      onClick={() => setActiveTab(id)}
      className={`flex items-center justify-between w-full px-4 py-3 rounded-xl cursor-pointer transition-all group ${
        activeTab === id 
          ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20' 
          : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-100'
      }`}
    >
      <div className="flex items-center gap-3">
        <Icon size={18} className={`transition-transform group-hover:scale-110 ${activeTab === id ? 'text-white' : 'text-slate-500'}`} />
        <span className="text-sm font-bold">{label}</span>
      </div>
      {badge && (
        <span className={`h-5 w-5 rounded-full text-[10px] font-bold flex items-center justify-center ${
          activeTab === id ? 'bg-white text-emerald-500' : 'bg-emerald-500 text-white animate-pulse'
        }`}>{badge}</span>
      )}
    </button>
  );

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-50 font-sans">
      {/* Role Picker Modal */}
      <AnimatePresence>
        {showRolePicker && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowRolePicker(false)}
            className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
          >
            <motion.div 
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl relative"
            >
              <h2 className="text-2xl font-bold mb-2">Switch Identity</h2>
              <p className="text-slate-400 text-sm mb-8">Select a coordinator or return to admin view.</p>
              
              <div className="space-y-3">
                <div 
                  onClick={() => handleIdentityChange({ id: 'admin', name: 'Global Admin', role: 'admin', dept: null })}
                  className={`w-full flex items-center gap-4 p-4 rounded-xl border cursor-pointer transition-all group ${
                    currentUser.id === 'admin' 
                      ? 'border-emerald-500 bg-emerald-500/10 shadow-[0_0_15px_rgba(16,185,129,0.1)]' 
                      : 'border-slate-800 bg-slate-800/50 hover:bg-slate-800 hover:border-emerald-500/50'
                  }`}
                >
                  <div className={`h-10 w-10 rounded-full flex items-center justify-center transition-transform group-hover:scale-110 ${
                    currentUser.id === 'admin' ? 'bg-emerald-500 text-white' : 'bg-emerald-500/10 text-emerald-500'
                  }`}>
                    <ShieldCheck size={20} />
                  </div>
                  <div className="text-left">
                    <p className="font-bold">Global Admin</p>
                    <p className="text-xs text-slate-500">Full Access (All Categories)</p>
                  </div>
                  <ChevronRight size={16} className={`ml-auto transition-colors ${currentUser.id === 'admin' ? 'text-emerald-500' : 'text-slate-600'}`} />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  {STAFF_LIST.map((staff) => (
                    <div 
                      key={staff.id}
                      onClick={() => handleIdentityChange({ ...staff })}
                      className={`flex flex-col gap-2 p-3 rounded-xl border cursor-pointer transition-all group ${
                        currentUser.id === staff.id 
                          ? 'border-emerald-500 bg-emerald-500/10 shadow-[0_0_15px_rgba(16,185,129,0.1)]' 
                          : 'border-slate-800 bg-slate-900 hover:bg-slate-800 hover:border-emerald-500/50'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`h-8 w-8 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110 ${
                          currentUser.id === staff.id ? 'bg-emerald-500 text-white' : 'bg-slate-800 text-slate-400'
                        }`}>
                          <staff.icon size={16} />
                        </div>
                        <div className="text-left overflow-hidden">
                          <p className="font-bold text-xs truncate">{staff.name}</p>
                          <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">{staff.role}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <button 
                onClick={() => setShowRolePicker(false)}
                className="mt-8 w-full py-3 text-slate-500 text-sm font-bold hover:text-white transition-colors"
              >
                Cancel
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 flex flex-col bg-slate-950 sticky top-0 h-screen">
        <div className="p-6">
          <div className="flex items-center gap-2 mb-8">
            <div className="h-8 w-8 bg-emerald-500 rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(16,185,129,0.3)]">
              <Droplets className="text-white" size={18} />
            </div>
            <span className="font-bold text-lg tracking-tight">Eco-Track</span>
          </div>
          
          <nav className="space-y-1">
            <SidebarItem id="overview" icon={LayoutDashboard} label="Dashboard" />
            <SidebarItem id="incidents" icon={AlertCircle} label="Active Alerts" />
            {currentUser.role === 'Head' && <SidebarItem id="delayed" icon={Clock} label="Delayed Tickets" />}
            <SidebarItem id="messages" icon={Bell} label="Alerts" badge={nudges.length > 0 ? nudges.length : null} />
            <SidebarItem id="analytics" icon={BarChart3} label="Analytics" />
            <SidebarItem id="areas" icon={Map} label="City Explorer" />
            {currentUser.role === 'admin' && <SidebarItem id="help" icon={HelpCircle} label="Help Center" badge={supportRequests.filter(r => r.status === 'Pending').length || null} />}
          </nav>
        </div>

        <div className="mt-auto p-6 border-t border-slate-800 bg-slate-900/20">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-10 w-10 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold ring-2 ring-emerald-500/20 shadow-inner">
              {currentUser.name?.charAt(0).toUpperCase() || 'A'}
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-bold truncate capitalize">{currentUser.name || 'Admin'}</p>
              <p className="text-[10px] text-emerald-500 font-bold uppercase tracking-widest">
                {currentUser.role === 'admin' ? 'Superuser' : `${currentUser.dept} ${currentUser.role}`}
              </p>
            </div>
          </div>
          <button 
            onClick={() => setShowRolePicker(true)}
            className="flex items-center justify-center gap-2 w-full py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg text-[10px] font-bold text-slate-400 hover:text-white transition-all uppercase tracking-widest"
          >
            <User size={12} /> Switch Identity
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative">
        <AnimatePresence>
          {notification && (
            <motion.div 
              initial={{ opacity: 0, y: 50, x: '-50%' }}
              animate={{ opacity: 1, y: 0, x: '-50%' }}
              exit={{ opacity: 0, y: 20, x: '-50%' }}
              className={`fixed bottom-12 left-1/2 z-[100] flex items-center gap-3 px-6 py-4 rounded-2xl shadow-2xl border ${
                notification.type === 'success' 
                  ? 'bg-emerald-500 border-emerald-400 text-white' 
                  : 'bg-rose-500 border-rose-400 text-white'
              }`}
            >
              {notification.type === 'success' ? <CheckCircle size={20} /> : <AlertTriangle size={20} />}
              <p className="font-bold text-sm tracking-tight">{notification.message}</p>
            </motion.div>
          )}
        </AnimatePresence>
        <header className="h-16 border-b border-slate-800 flex items-center justify-between px-8 bg-slate-950/50 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-4 text-sm text-slate-400">
            <span className="opacity-50">Eco-Track</span>
            <span className="text-slate-800">/</span>
            <span className="text-slate-100 font-bold tracking-tight capitalize">{activeTab}</span>
            {currentUser.dept && (
              <>
                <span className="text-slate-800">/</span>
                <span className="text-emerald-500 font-bold uppercase text-[10px] tracking-widest">{currentUser.dept} Only</span>
              </>
            )}
          </div>
          
          <div className="flex items-center gap-4">
            <div className="relative group hidden md:block">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-600 group-focus-within:text-emerald-500 transition-colors" />
              <input 
                type="text" 
                placeholder="Search alerts..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="h-9 w-64 bg-slate-900/50 border border-slate-800 rounded-lg pl-9 text-xs focus:outline-none focus:ring-1 focus:ring-emerald-500/50 transition-all"
              />
            </div>
            <button className="h-9 w-9 rounded-lg border border-slate-800 flex items-center justify-center hover:bg-slate-900 transition-colors relative">
              <Bell size={16} className="text-slate-500" />
              <span className="absolute top-2 right-2 h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
            </button>
          </div>
        </header>

        <div className="p-8 max-w-7xl w-full mx-auto">
          {loading && !stats ? (
            <div className="h-[60vh] flex flex-col items-center justify-center gap-4 text-slate-500">
              <div className="h-10 w-10 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-sm font-medium animate-pulse">Syncing Secure Environment...</p>
            </div>
          ) : (
            <AnimatePresence mode="wait">
              {activeTab === 'overview' && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-8"
                >
                  <div className="flex items-end justify-between">
                    <div>
                      <h2 className="text-3xl font-bold tracking-tight">
                        {currentUser.role === 'admin' ? 'City Overview' : `${currentUser.dept} Monitor`}
                      </h2>
                      <p className="text-slate-400">
                        {currentUser.role === 'admin' 
                          ? 'Global resource management and incident tracking.' 
                          : `Specialized monitoring for the ${currentUser.dept} department.`}
                      </p>
                    </div>
                    <button 
                      onClick={() => window.print()}
                      className="bg-slate-50 text-slate-950 px-4 py-2 rounded-lg text-sm font-bold hover:bg-slate-200 transition-colors shadow-lg"
                    >
                      Generate PDF
                    </button>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <StatCard 
                      title="Citizens Impacted" 
                      value={stats?.stats?.users || 0} 
                      change="+12%" 
                      icon={Users} 
                      onClick={() => { if(currentUser.role === 'admin') { setSelectedDept(null); setSelectedStatus(null); }}}
                      active={!selectedDept && !selectedStatus}
                    />
                    <StatCard 
                      title="Active Tickets" 
                      value={currentUser.role === 'admin' ? stats?.stats?.pending : stats?.dept_pending?.[currentUser.dept?.toLowerCase() || '']} 
                      change="+2" 
                      icon={AlertCircle} 
                      destructive 
                      onClick={() => setSelectedStatus(selectedStatus === 'Open' ? null : 'Open')}
                      active={selectedStatus === 'Open'}
                    />
                    <StatCard 
                      title="Resolved Today" 
                      value={stats?.stats?.resolved} 
                      change="+18%" 
                      icon={CheckCircle2} 
                      onClick={() => setSelectedStatus(selectedStatus === 'Resolved' ? null : 'Resolved')}
                      active={selectedStatus === 'Resolved'}
                    />
                    <StatCard title="Eco-Score" value="84" change="+4" icon={Award} />
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-7 gap-6">
                    {/* Charts */}
                    <div className="lg:col-span-4 rounded-2xl border border-slate-800 bg-slate-900/40 p-8 shadow-sm backdrop-blur-sm">
                      <div className="flex items-center justify-between mb-8">
                        <div>
                          <h3 className="font-bold text-lg">Activity Trends</h3>
                          <p className="text-xs text-slate-500 font-medium">Categorized resolve metrics</p>
                        </div>
                      </div>
                      <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={stats?.historical_data || []}>
                            <defs>
                              <linearGradient id="colorBrand" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.1}/>
                                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                            <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                            <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                            <Tooltip 
                              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', fontSize: '12px' }}
                            />
                            <Area type="monotone" dataKey="value" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorBrand)" />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Department Distribution (Hidden for Coordinators) */}
                    <div className="lg:col-span-3 rounded-2xl border border-slate-800 bg-slate-900/40 p-8 shadow-sm">
                      <h3 className="font-bold text-lg mb-6">Department Distribution</h3>
                      <div className="space-y-6">
                        <DeptProgress label="Electricity" value={stats?.dept_pending?.electrical} total={stats?.stats?.pending} icon={Zap} active={currentUser.dept === 'Electricity' || currentUser.role === 'admin'} />
                        <DeptProgress label="Water Resources" value={stats?.dept_pending?.water} total={stats?.stats?.pending} icon={Droplets} active={currentUser.dept === 'Water' || currentUser.role === 'admin'} />
                        <DeptProgress label="Waste Management" value={stats?.dept_pending?.sewage} total={stats?.stats?.pending} icon={Trash2} active={currentUser.dept === 'Sewage' || currentUser.role === 'admin'} />
                      </div>
                      
                      <div className="mt-8 p-5 bg-emerald-500/5 border border-emerald-500/10 rounded-xl">
                        <p className="text-xs text-emerald-500 font-bold mb-1 flex items-center gap-2 uppercase tracking-widest">
                          <TrendingUp size={14} /> LIVE STATUS
                        </p>
                        <p className="text-[10px] text-slate-500 font-medium leading-relaxed">
                          System efficiency is at 94%. Current response time is under 12 minutes for prioritized alerts.
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Incident List */}
                  <div className="space-y-6 pt-4">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-xl font-bold">Category Incident Feed</h3>
                          {(selectedDept || selectedStatus) && (
                            <span className="text-[10px] px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-500 font-bold border border-emerald-500/10 uppercase tracking-widest animate-pulse">
                              Filtered: {selectedStatus || selectedDept}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-slate-500">Real-time alerts for {currentUser.dept || 'All Categories'}.</p>
                      </div>
                      
                      {currentUser.role === 'admin' && (
                        <div className="flex gap-1 bg-slate-900/50 p-1.5 rounded-xl border border-slate-800 shadow-inner">
                          {['All', 'Electricity', 'Water', 'Sewage'].map((dept) => (
                            <button
                              key={dept}
                              onClick={() => setSelectedDept(dept === 'All' ? null : dept)}
                              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                                (selectedDept === dept || (dept === 'All' && !selectedDept))
                                  ? 'bg-slate-800 text-white shadow-lg' 
                                  : 'text-slate-500 hover:text-slate-300'
                              }`}
                            >
                              {dept}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {reports.filter(r => 
                        r.issue_type.toLowerCase().includes(searchQuery.toLowerCase()) || 
                        r.location.toLowerCase().includes(searchQuery.toLowerCase())
                      ).length > 0 ? (
                        reports.filter(r => 
                          r.issue_type.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          r.location.toLowerCase().includes(searchQuery.toLowerCase())
                        ).map((report) => (
                          <ReportCard 
                            key={report._id} 
                            report={report} 
                            onResolve={() => handleResolve(report._id)} 
                            onView={() => setSelectedReport(report)}
                          />
                        ))
                      ) : (
                        <div className="col-span-full py-20 rounded-2xl border border-slate-800 border-dashed bg-slate-900/20 flex flex-col items-center justify-center text-slate-600">
                          <Filter size={40} className="mb-4 opacity-10" />
                          <p className="text-sm font-bold">No matching alerts found.</p>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}

              {activeTab === 'incidents' && (
                <motion.div 
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-8"
                >
                  <div className="flex items-end justify-between">
                    <div>
                      <h2 className="text-3xl font-bold tracking-tight">Departmental Alerts</h2>
                      <p className="text-slate-400">Comprehensive list of tickets assigned to your department.</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {reports.map((report) => (
                      <ReportCard 
                        key={report._id} 
                        report={report} 
                        onResolve={() => handleResolve(report._id)} 
                        onView={() => setSelectedReport(report)}
                      />
                    ))}
                  </div>
                </motion.div>
              )}

              {activeTab === 'delayed' && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-8"
                >
                  <div className="flex items-end justify-between">
                    <div>
                      <h2 className="text-3xl font-bold tracking-tight text-rose-500 flex items-center gap-3">
                        <AlertTriangle size={32} /> Delayed Tickets
                      </h2>
                      <p className="text-slate-400">Issues pending for more than 24 hours. Immediate action required.</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {reports.map((report) => (
                      <ReportCard 
                        key={report._id} 
                        report={report} 
                        onResolve={() => handleResolve(report._id)} 
                        onNudge={() => handleNudge(report.report_id)}
                        onView={() => setSelectedReport(report)}
                        canNudge={currentUser.role === 'Head'}
                        forceDelayed 
                      />
                    ))}
                    {reports.length === 0 && (
                      <div className="col-span-full py-20 rounded-2xl border border-slate-800 border-dashed bg-slate-900/20 flex flex-col items-center justify-center text-slate-600">
                        <CheckCircle size={40} className="mb-4 text-emerald-500/20" />
                        <p className="text-sm font-bold">No delayed alerts for your department.</p>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}

              {activeTab === 'messages' && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-8"
                >
                  <div>
                    <h2 className="text-3xl font-bold tracking-tight">Internal Alerts</h2>
                    <p className="text-slate-400">Direct intimations from Departmental Head.</p>
                  </div>

                  <div className="max-w-4xl space-y-4">
                    {nudges.map((nudge) => (
                      <div key={nudge._id} className="p-5 rounded-2xl border border-slate-800 bg-slate-900/50 flex items-start gap-4 hover:border-emerald-500/30 transition-all group">
                        <div className="h-10 w-10 rounded-xl bg-rose-500/10 text-rose-500 flex items-center justify-center flex-shrink-0 group-hover:bg-rose-500 group-hover:text-white transition-colors">
                          <Bell size={20} />
                        </div>
                        <div className="flex-1">
                          <div className="flex justify-between items-start mb-1">
                            <h4 className="font-bold text-slate-100 flex items-center gap-2">
                              {nudge.message}
                              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-emerald-400 font-mono">{nudge.report_id}</span>
                            </h4>
                            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{new Date(nudge.timestamp).toLocaleTimeString()}</span>
                          </div>
                          <p className="text-xs text-slate-400 leading-relaxed">Please ensure this issue is processed immediately. Delayed reports impact our overall efficiency score.</p>
                        </div>
                      </div>
                    ))}
                    {nudges.length === 0 && (
                      <div className="py-20 rounded-2xl border border-slate-800 border-dashed bg-slate-900/20 flex flex-col items-center justify-center text-slate-600">
                        <Bell size={40} className="mb-4 opacity-20" />
                        <p className="text-sm font-bold">No new alerts from Head.</p>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}

              {activeTab === 'areas' && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-8"
                >
                  <div className="flex items-end justify-between">
                    <div>
                      <h2 className="text-3xl font-bold tracking-tight">City Explorer</h2>
                      <p className="text-slate-400">Public display board for neighborhood insights.</p>
                    </div>
                    <select 
                      value={selectedAreaId || ''} 
                      onChange={(e) => setSelectedAreaId(e.target.value)}
                      className="bg-slate-800 border border-slate-700 text-white px-4 py-2 rounded-lg text-sm font-bold outline-none"
                    >
                      {areas.map(area => (
                        <option key={area.area_id} value={area.area_id}>{area.name}</option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <StatCard title="Eco-Score" value={areaStats?.score || 100} icon={Shield} change="+2" active />
                    <StatCard title="Active Issues" value={areaStats?.pending || 0} icon={AlertCircle} destructive />
                    <StatCard title="Fixed Locally" value={areaStats?.resolved || 0} icon={CheckCircle2} change="WEEKLY" />
                    <StatCard title="Resource Saved" value={`${areaStats?.impact || 0}L`} icon={Droplets} change="LIVE" />
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-8">
                      <h3 className="font-bold text-lg mb-6">Local Incident Feed</h3>
                      <div className="space-y-4">
                        {reports.filter(r => r.area_id === selectedAreaId).length > 0 ? (
                          reports.filter(r => r.area_id === selectedAreaId).slice(0, 5).map(report => (
                            <div 
                              key={report._id} 
                              onClick={() => setSelectedReport(report)}
                              className="flex items-center justify-between p-4 bg-slate-800/40 rounded-xl border border-slate-800 cursor-pointer hover:border-emerald-500/50 transition-all"
                            >
                              <div className="flex items-center gap-4">
                                <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
                                <div>
                                  <p className="text-sm font-bold">{report.issue_type}</p>
                                  <p className="text-[10px] text-slate-500">{report.location}</p>
                                </div>
                              </div>
                              <span className="text-[10px] font-bold text-slate-500 uppercase">{report.status}</span>
                            </div>
                          ))
                        ) : (
                          <p className="text-center py-10 text-slate-600 text-sm italic">Everything looks clean in this neighborhood!</p>
                        )}
                      </div>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-8">
                      <div className="flex items-center justify-between mb-8">
                        <h3 className="font-bold text-lg">Neighborhood Hotspots</h3>
                        <div className="px-3 py-1 rounded-full bg-rose-500/10 text-rose-500 text-[10px] font-bold uppercase tracking-widest animate-pulse">
                          Critical Focus
                        </div>
                      </div>
                      <div className="space-y-6">
                        {hotspots.map((spot, idx) => (
                          <div key={idx} className="relative pl-8 before:content-[''] before:absolute before:left-0 before:top-0 before:bottom-0 before:w-1 before:bg-slate-800 before:rounded-full">
                            <div className="absolute left-[-4px] top-0 h-3 w-3 rounded-full bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.5)]"></div>
                            <div className="flex justify-between items-start mb-1">
                              <p className="text-sm font-bold text-slate-200">{spot.location}</p>
                              <span className="text-[10px] font-bold text-rose-500 bg-rose-500/10 px-2 py-0.5 rounded-md">{spot.count} Reports</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] text-slate-500 font-medium uppercase tracking-wider">Primary Issue:</span>
                              <span className="text-[10px] text-emerald-500 font-bold">{spot.primary_issue}</span>
                            </div>
                          </div>
                        ))}
                        {hotspots.length === 0 && (
                          <div className="py-10 flex flex-col items-center justify-center text-slate-600 border border-slate-800 border-dashed rounded-xl">
                            <Shield size={32} className="mb-2 opacity-20" />
                            <p className="text-xs italic">No critical hotspots detected.</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              {activeTab === 'analytics' && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-8"
                >
                  <div className="flex items-end justify-between">
                    <div>
                      <h2 className="text-3xl font-bold tracking-tight">Resource Analytics</h2>
                      <p className="text-slate-400">Deep-dive into city-wide consumption and response metrics.</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/40 p-8 shadow-sm">
                      <h3 className="font-bold text-lg mb-8">Resource Consumption Over Time</h3>
                      <div className="h-[400px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={stats?.historical_data || []}>
                            <defs>
                              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.1}/>
                                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                            <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                            <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                            <Tooltip 
                              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', fontSize: '12px' }}
                            />
                            <Area type="monotone" dataKey="value" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    <div className="space-y-6">
                      <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6 shadow-sm">
                        <h3 className="font-bold text-sm text-slate-400 uppercase tracking-widest mb-6">Efficiency metrics</h3>
                        <div className="space-y-6">
                          <EfficiencyMetric label="Avg. Response Time" value="12m" target="15m" percent={80} />
                          <EfficiencyMetric label="Resolution Rate" value={`${stats?.efficiency?.electrical || 0}%`} target="90%" percent={stats?.efficiency?.electrical || 0} />
                          <EfficiencyMetric label="Citizen Satisfaction" value="4.8/5" target="4.5/5" percent={96} />
                        </div>
                      </div>

                      <div className="rounded-2xl border border-slate-800 bg-emerald-500/5 p-6 shadow-sm border-dashed">
                        <div className="flex items-center gap-3 mb-4">
                          <div className="h-10 w-10 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-500">
                            <TrendingUp size={20} />
                          </div>
                          <div>
                            <p className="font-bold text-sm">Performance Peak</p>
                            <p className="text-xs text-slate-500">Highest efficiency recorded today</p>
                          </div>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">
                          Your department has surpassed the weekly resolution target by <span className="text-emerald-500 font-bold">14%</span>. Maintain this pace to unlock community rewards.
                        </p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              
              {activeTab === 'help' && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-8"
                >
                  <div>
                    <h2 className="text-3xl font-bold tracking-tight">Citizen Help Center</h2>
                    <p className="text-slate-400">Review and respond to messages from citizens.</p>
                  </div>

                  {/* Help Tabs */}
                  <div className="flex gap-2 p-1 bg-slate-900 w-fit rounded-xl border border-slate-800">
                    <button 
                      onClick={() => setSupportTab('active')}
                      className={`px-6 py-2 rounded-lg text-xs font-bold transition-all ${
                        supportTab === 'active' ? 'bg-emerald-500 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'
                      }`}
                    >
                      Active Messages ({supportRequests.filter(r => r.status === 'Pending').length})
                    </button>
                    <button 
                      onClick={() => setSupportTab('resolved')}
                      className={`px-6 py-2 rounded-lg text-xs font-bold transition-all ${
                        supportTab === 'resolved' ? 'bg-slate-800 text-white' : 'text-slate-500 hover:text-slate-300'
                      }`}
                    >
                      Resolved
                    </button>
                  </div>

                  <div className="grid grid-cols-1 gap-4 max-w-4xl">
                    {supportRequests
                      .filter(req => supportTab === 'active' ? req.status === 'Pending' : req.status === 'Resolved')
                      .map((req) => (
                      <div key={req._id} className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 hover:border-emerald-500/30 transition-all group">
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-500 font-bold">
                              {req.name?.charAt(0) || 'U'}
                            </div>
                            <div>
                              <p className="font-bold text-slate-100">{req.name || 'Anonymous'}</p>
                              <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{req.area_name} • ID: {req.user_id}</p>
                            </div>
                          </div>
                          <span className="text-[10px] text-slate-500 font-bold">{new Date(req.timestamp).toLocaleString()}</span>
                        </div>
                        <div className="pl-13">
                          <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800/50 relative">
                             <MessageCircle size={14} className="absolute -left-7 top-4 text-slate-600" />
                             <p className="text-sm text-slate-300 leading-relaxed italic">"{req.message}"</p>
                          </div>
                          <div className="mt-4 flex items-center gap-3">
                            <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-widest ${
                              req.status === 'Pending' ? 'bg-amber-500/10 text-amber-500' : 'bg-emerald-500/10 text-emerald-500'
                            }`}>{req.status}</span>
                            {req.status === 'Pending' && (
                              <button 
                                onClick={() => handleResolveSupport(req._id)}
                                className="text-[10px] font-bold text-slate-500 hover:text-emerald-500 transition-colors uppercase tracking-widest"
                              >
                                Mark as Resolved
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                    {supportRequests.filter(req => supportTab === 'active' ? req.status === 'Pending' : req.status === 'Resolved').length === 0 && (
                      <div className="py-20 rounded-2xl border border-slate-800 border-dashed bg-slate-900/20 flex flex-col items-center justify-center text-slate-600">
                        <HelpCircle size={40} className="mb-4 opacity-20" />
                        <p className="text-sm font-bold">No {supportTab} help requests from citizens.</p>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}

            </AnimatePresence>
          )}
        </div>
        <AnimatePresence>
          {selectedReport && (
            <ReportDetailModal 
              report={selectedReport} 
              onClose={() => setSelectedReport(null)} 
              onResolve={() => {
                handleResolve(selectedReport._id);
                setSelectedReport(null);
              }}
            />
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

const StatCard = ({ title, value, change, icon: Icon, destructive, onClick, active }) => (
  <div 
    onClick={onClick}
    className={`rounded-2xl border p-6 shadow-md transition-all cursor-pointer group ${
      active 
        ? 'border-emerald-500 bg-emerald-500/5 ring-1 ring-emerald-500/20' 
        : 'border-slate-800 bg-slate-900/40 hover:bg-slate-900/60 hover:border-slate-700'
    }`}
  >
    <div className="flex items-center justify-between mb-4">
      <span className={`text-[10px] font-bold uppercase tracking-widest ${active ? 'text-emerald-500' : 'text-slate-500'}`}>
        {title}
      </span>
      <div className={`p-2 rounded-lg ${active ? 'bg-emerald-500/20 text-emerald-500' : 'bg-slate-800 text-slate-400'} group-hover:scale-110 transition-transform`}>
        <Icon size={16} className={destructive && !active ? 'text-rose-500' : ''} />
      </div>
    </div>
    <div className="flex items-baseline gap-2">
      <span className="text-3xl font-bold tracking-tight">{value}</span>
      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${destructive ? 'bg-rose-500/10 text-rose-500' : 'bg-emerald-500/10 text-emerald-500'}`}>
        {change}
      </span>
    </div>
  </div>
);

const DeptProgress = ({ label, value, total, icon: Icon, active }) => {
  const percent = total > 0 ? (value / total) * 100 : 0;
  return (
    <div className={`space-y-3 transition-opacity ${active ? 'opacity-100' : 'opacity-30'}`}>
      <div className="flex justify-between text-xs">
        <div className="flex items-center gap-2 font-bold text-slate-200">
          <Icon size={14} className={active ? 'text-emerald-500' : 'text-slate-500'} />
          <span>{label}</span>
        </div>
        <span className="text-slate-500 font-bold">{value} Alerts</span>
      </div>
      <div className="h-1.5 w-full bg-slate-800/50 rounded-full overflow-hidden">
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: `${percent}%` }}
          className={`h-full ${active ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'bg-slate-700'}`}
        />
      </div>
    </div>
  );
};

const EfficiencyMetric = ({ label, value, target, percent }) => (
  <div className="space-y-3">
    <div className="flex justify-between items-end">
      <div>
        <p className="text-xs text-slate-500 font-bold uppercase tracking-widest mb-1">{label}</p>
        <p className="text-xl font-bold">{value}</p>
      </div>
      <div className="text-right">
        <p className="text-[10px] text-slate-600 font-bold uppercase tracking-widest">Target</p>
        <p className="text-xs font-bold text-slate-400">{target}</p>
      </div>
    </div>
    <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
      <motion.div 
        initial={{ width: 0 }}
        animate={{ width: `${percent}%` }}
        className="h-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.3)]"
      />
    </div>
  </div>
);

const ReportDetailModal = ({ report, onClose, onResolve }) => {
  if (!report) return null;
  const reportedDate = new Date(report.timestamp);
  const resolvedDate = report.resolved_at ? new Date(report.resolved_at) : null;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
      className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
    >
      <motion.div 
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden"
      >
        {/* Background Glow */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl -mr-32 -mt-32"></div>
        
        <div className="flex justify-between items-start mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="px-3 py-1 rounded-full bg-slate-800 text-emerald-500 border border-emerald-500/20 text-[10px] font-bold uppercase tracking-widest">
                {report.topic_id?.split('_')[0] || 'GENERAL'}
              </span>
              <span className="text-xs font-mono text-slate-500">#{report.report_id}</span>
            </div>
            <h2 className="text-3xl font-bold text-slate-100">{report.issue_type}</h2>
          </div>
          <button 
            onClick={onClose}
            className="h-10 w-10 rounded-xl bg-slate-800 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 transition-all"
          >
            <AlertCircle size={20} className="rotate-45" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="h-10 w-10 rounded-xl bg-slate-800 flex items-center justify-center text-slate-400">
                <Map size={20} />
              </div>
              <div>
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Location Details</p>
                <p className="text-sm text-slate-200">{report.location}</p>
                {report.landmark && <p className="text-xs text-slate-500 mt-1">Landmark: {report.landmark}</p>}
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="h-10 w-10 rounded-xl bg-slate-800 flex items-center justify-center text-slate-400">
                <Clock size={20} />
              </div>
              <div>
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Reporting Timeline</p>
                <p className="text-sm text-slate-200">
                  Reported on {reportedDate.toLocaleDateString()} at {reportedDate.toLocaleTimeString()}
                </p>
                {resolvedDate && (
                  <p className="text-sm text-emerald-500 mt-1 font-medium">
                    Resolved on {resolvedDate.toLocaleDateString()} at {resolvedDate.toLocaleTimeString()}
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="h-10 w-10 rounded-xl bg-slate-800 flex items-center justify-center text-slate-400">
                <User size={20} />
              </div>
              <div>
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Reporter</p>
                <p className="text-sm text-slate-200">User ID: {report.user_id}</p>
                <p className="text-xs text-slate-500 mt-1">Neighborhood Area: {report.area_id}</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="h-10 w-10 rounded-xl bg-slate-800 flex items-center justify-center text-slate-400">
                <Shield size={20} />
              </div>
              <div>
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Current Status</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className={`h-2 w-2 rounded-full ${report.status === 'Resolved' ? 'bg-emerald-500' : 'bg-rose-500 animate-pulse'}`}></div>
                  <span className={`text-sm font-bold uppercase tracking-widest ${report.status === 'Resolved' ? 'text-emerald-500' : 'text-rose-500'}`}>
                    {report.status}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4 pt-8 border-t border-slate-800">
          {report.status !== 'Resolved' ? (
            <button 
              onClick={onResolve}
              className="flex-1 py-4 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-2xl shadow-lg shadow-emerald-500/20 transition-all uppercase tracking-widest text-sm"
            >
              Resolve Issue Now
            </button>
          ) : (
            <div className="flex-1 py-4 bg-slate-800 text-slate-400 font-bold rounded-2xl flex items-center justify-center gap-2 uppercase tracking-widest text-sm">
              <CheckCircle size={18} /> Issue Resolved
            </div>
          )}
          <button 
            onClick={onClose}
            className="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-2xl transition-all uppercase tracking-widest text-sm"
          >
            Close
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};

const ReportCard = ({ report, onResolve, onNudge, canNudge, forceDelayed, onView }) => {
  const reportedDate = new Date(report.timestamp);
  const resolvedDate = report.resolved_at ? new Date(report.resolved_at) : null;
  const isDelayed = forceDelayed || (report.status === 'Open' && (new Date() - reportedDate > 24 * 60 * 60 * 1000));

  return (
    <motion.div 
      layout
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      onClick={onView}
      className={`rounded-2xl border p-6 shadow-sm transition-all group relative overflow-hidden cursor-pointer ${
        report.status === 'Resolved' 
          ? 'border-slate-800 bg-slate-900/20 opacity-60' 
          : isDelayed 
            ? 'border-rose-500/30 bg-rose-500/5 shadow-[0_0_20px_rgba(244,63,94,0.05)]'
            : 'border-slate-800 bg-slate-900/40 hover:shadow-emerald-500/5 hover:border-slate-700'
      }`}
    >
      {isDelayed && report.status !== 'Resolved' && (
        <div className="absolute top-0 right-0 p-1 px-3 bg-rose-500 text-white text-[8px] font-bold uppercase tracking-widest rounded-bl-lg">
          Delayed &gt; 24h
        </div>
      )}
      
      <div className="flex justify-between items-start mb-6">
        <div className="flex flex-col gap-2">
          <span className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 border border-slate-700 text-[10px] font-bold tracking-widest uppercase w-fit">
            {report.topic_id?.split('_')[0] || 'GENERAL'}
          </span>
          <div className="flex items-center gap-1.5">
            <div className="h-1 w-3 rounded-full bg-emerald-500/50"></div>
            <span className="text-[13px] font-mono text-emerald-400 font-bold tracking-[0.1em] drop-shadow-[0_0_8px_rgba(52,211,153,0.3)]">
              {report.report_id}
            </span>
          </div>
        </div>
        <div className="text-right">
          <p className="text-[9px] font-bold text-slate-500 uppercase tracking-tighter">Reported</p>
          <span className="text-[10px] font-bold text-slate-300">
            {reportedDate.toLocaleDateString([], { month: 'short', day: 'numeric' })} {reportedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>
      
      <div className="space-y-1 mb-8">
        <h4 className={`font-bold text-lg leading-tight transition-colors ${
          report.status === 'Resolved' ? 'text-slate-500' : 'text-slate-100 group-hover:text-emerald-500'
        }`}>{report.issue_type}</h4>
        <div className="text-[11px] text-slate-500 font-medium flex items-center gap-2 mt-2">
          <div className="h-1.5 w-1.5 rounded-full bg-slate-700"></div> {report.location}
        </div>
      </div>

      <div className="flex items-center justify-between pt-5 border-t border-slate-800/50 gap-2">
        <div className="flex items-center gap-2">
          <div className="relative">
            <div className={`h-2 w-2 rounded-full ${report.status === 'Resolved' ? 'bg-slate-600' : isDelayed ? 'bg-rose-500' : 'bg-emerald-500'}`}></div>
            {report.status !== 'Resolved' && <div className={`absolute inset-0 h-2 w-2 rounded-full ${isDelayed ? 'bg-rose-500' : 'bg-emerald-500'} animate-ping`}></div>}
          </div>
          <div>
            <span className={`text-[10px] font-bold uppercase tracking-widest block ${
              report.status === 'Resolved' ? 'text-slate-500' : isDelayed ? 'text-rose-500' : 'text-emerald-500'
            }`}>{report.status}</span>
            {resolvedDate && (
              <span className="text-[8px] text-slate-500 font-bold uppercase">at {resolvedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {canNudge && isDelayed && report.status !== 'Resolved' && (
            <button 
              onClick={(e) => { e.stopPropagation(); onNudge(); }}
              className="text-[10px] font-bold p-2 rounded-lg bg-slate-800 text-rose-400 border border-slate-700 hover:bg-rose-500 hover:text-white hover:border-rose-500 transition-all"
              title="Nudge Staff"
            >
              <Bell size={14} />
            </button>
          )}
          {report.status !== 'Resolved' && (
            <button 
              onClick={(e) => { e.stopPropagation(); onResolve(); }}
              className={`text-[10px] font-bold px-4 py-2 rounded-lg transition-all border shadow-lg ${
                isDelayed 
                  ? 'bg-rose-500 text-white border-rose-400 hover:bg-rose-600' 
                  : 'bg-slate-800 hover:bg-emerald-500 hover:text-white text-slate-100 border-slate-700 hover:border-emerald-500'
              }`}
            >
              PROCESS
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default App;
