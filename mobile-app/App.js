import React, { useState, useEffect } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  TouchableOpacity, 
  ScrollView, 
  TextInput, 
  ActivityIndicator, 
  StatusBar,
  Dimensions,
  SafeAreaView,
  Platform,
  Animated
} from 'react-native';
import { 
  Droplets, 
  Zap, 
  Trash2, 
  ChevronRight, 
  ChevronLeft, 
  MapPin, 
  AlertCircle, 
  CheckCircle2, 
  BarChart3, 
  User,
  Shield,
  ArrowRight,
  Clock,
  History,
  Settings,
  Award,
  Home,
  Menu,
  Bell,
  Search,
  Plus
} from 'lucide-react-native';
import axios from 'axios';

const { width, height } = Dimensions.get('window');

const COLORS = {
  primary: '#10b981',
  background: '#0f172a',
  card: '#1e293b',
  cardBorder: '#334155',
  text: '#f8fafc',
  textSecondary: '#94a3b8',
  danger: '#f43f5e',
  accent: '#3b82f6',
  header: '#1e293b'
};

// IMPORTANT: Replace with your actual local IP address from ipconfig
const API_BASE = 'http://192.168.31.222:8000/api';

const RESOURCES = [
  { key: 'water', label: '💧 Water', icon: Droplets, color: '#3b82f6' },
  { key: 'electricity', label: '⚡ Electricity', icon: Zap, color: '#eab308' },
  { key: 'sewage', label: '🗑 Waste', icon: Trash2, color: '#10b981' }
];

const ISSUE_OPTIONS = {
  water: ["Leak 💧", "Overflow 🌊", "Misuse 🚿", "Other ❓"],
  electricity: ["Light Left On 💡", "Illegal Usage ⚡", "Overuse 🔌", "Other ❓"],
  sewage: ["Garbage Pile 🗑", "No Segregation ♻️", "Overflow Bin 🚮", "Other ❓"]
};

export default function App() {
  const [screen, setScreen] = useState('home');
  const [reportStep, setReportStep] = useState('category');
  const [loading, setLoading] = useState(false);
  const [areaStats, setAreaStats] = useState(null);
  const [pincode, setPincode] = useState('');
  const [localities, setLocalities] = useState([]);
  const [selectedLocality, setSelectedLocality] = useState(null);
  const [landmark, setLandmark] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [selectedIssueDetail, setSelectedIssueDetail] = useState(null);
  const [myReports, setMyReports] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);
  const [currentUser, setCurrentUser] = useState({ id: 12345678, name: 'Eco Citizen', area_id: 'Indiranagar' });

  useEffect(() => {
    fetchData();
  }, [screen]);

  const fetchData = async () => {
    try {
      if (screen === 'home') {
        const [statsRes, reportsRes, overviewRes] = await Promise.all([
          axios.get(`${API_BASE}/areas/${currentUser.area_id}/stats`).catch(() => ({ data: null })),
          axios.get(`${API_BASE}/reports`).catch(() => ({ data: [] })),
          axios.get(`${API_BASE}/overview`).catch(() => ({ data: null }))
        ]);
        setAreaStats(statsRes.data);
        setMyReports(reportsRes.data);
        setHistoricalData(overviewRes.data?.historical_data || []);
      }
    } catch (err) {
      console.log('Fetch error:', err.message);
    }
  };

  const handlePincodeSubmit = async () => {
    if (pincode.length !== 6) return;
    setLoading(true);
    try {
      const res = await axios.get(`https://api.postalpincode.in/pincode/${pincode}`);
      if (res.data[0].Status === 'Success') {
        setLocalities(res.data[0].PostOffice);
        setReportStep('locality');
      } else {
        alert('Invalid Pincode');
      }
    } catch (err) {
      alert('Pincode service error');
    } finally {
      setLoading(false);
    }
  };

  const [successAnim] = useState(new Animated.Value(0));

  const showSuccess = () => {
    setScreen('success');
    Animated.spring(successAnim, {
      toValue: 1,
      tension: 50,
      friction: 7,
      useNativeDriver: true,
    }).start();

    setTimeout(() => {
      Animated.timing(successAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }).start(() => {
        setScreen('home');
        resetFlow();
      });
    }, 3000);
  };

  const submitReport = async () => {
    setLoading(true);
    try {
      const reportData = {
        user_id: currentUser.id,
        res_key: selectedCategory.key,
        issue_text: selectedIssue,
        locality: selectedLocality.Name,
        pincode: pincode,
        landmark: landmark,
        location: `${selectedLocality.Name}, Near ${landmark}`,
      };
      
      console.log('Submitting to:', `${API_BASE}/reports/submit`);
      await axios.post(`${API_BASE}/reports/submit`, reportData);
      showSuccess();
    } catch (err) {
      console.log('Report submission error:', err);
      if (err.response) {
        console.log('Error Data:', err.response.data);
        console.log('Error Status:', err.response.status);
      }
      alert(`Report submission failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const resetFlow = () => {
    setReportStep('category');
    setSelectedCategory(null);
    setSelectedIssue(null);
    setLandmark('');
    setPincode('');
    setSelectedLocality(null);
  };

  const Header = ({ title }) => (
    <View style={styles.appHeader}>
      <TouchableOpacity>
        <Menu color={COLORS.text} size={24} />
      </TouchableOpacity>
      <Text style={styles.headerTitleText}>{title}</Text>
      <TouchableOpacity>
        <Bell color={COLORS.text} size={24} />
      </TouchableOpacity>
    </View>
  );

  const [detailAnim] = useState(new Animated.Value(0));

  useEffect(() => {
    if (selectedIssueDetail) {
      Animated.spring(detailAnim, {
        toValue: 1,
        tension: 50,
        friction: 8,
        useNativeDriver: true,
      }).start();
    } else {
      Animated.timing(detailAnim, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }).start();
    }
  }, [selectedIssueDetail]);

  const renderHistory = () => (
    <View style={styles.mainContent}>
      <Header title="All Reports" />
      <ScrollView style={styles.scrollContainer} contentContainerStyle={{ paddingBottom: 100 }}>
        {myReports.length === 0 ? (
          <View style={styles.emptyState}>
            <Clock color={COLORS.textSecondary} size={48} />
            <Text style={styles.emptyText}>No reports found.</Text>
          </View>
        ) : (
          myReports.map((r, i) => (
            <TouchableOpacity key={i} style={styles.issueListItem} onPress={() => setSelectedIssueDetail(r)}>
              <View style={[styles.statusIndicator, { backgroundColor: r.status === 'Resolved' ? COLORS.primary : COLORS.danger }]} />
              <View style={styles.issueListInfo}>
                <Text style={styles.issueListType}>{r.issue_type || 'General Issue'}</Text>
                <Text style={styles.issueListLoc}>{r.locality || r.area_id}</Text>
                <Text style={styles.issueListTime}>{r.timestamp ? new Date(r.timestamp).toLocaleDateString() : 'Recent'}</Text>
              </View>
              <View style={[styles.statusBadge, { backgroundColor: r.status === 'Resolved' ? COLORS.primary + '15' : COLORS.danger + '15' }]}>
                <Text style={[styles.statusBadgeText, { color: r.status === 'Resolved' ? COLORS.primary : COLORS.danger }]}>
                  {r.status}
                </Text>
              </View>
              <ChevronRight color={COLORS.cardBorder} size={20} />
            </TouchableOpacity>
          ))
        )}
      </ScrollView>
    </View>
  );

  const renderIssueDetail = () => (
    <View style={styles.detailOverlay}>
      <TouchableOpacity style={StyleSheet.absoluteFill} onPress={() => setSelectedIssueDetail(null)} />
      <Animated.View style={[
        styles.detailCard,
        {
          transform: [{
            translateY: detailAnim.interpolate({
              inputRange: [0, 1],
              outputRange: [600, 0]
            })
          }]
        }
      ]}>
        <View style={styles.detailHeader}>
          <Text style={styles.detailTitle}>Issue Details</Text>
          <TouchableOpacity onPress={() => setSelectedIssueDetail(null)}>
            <Plus color={COLORS.textSecondary} size={24} style={{ transform: [{ rotate: '45deg' }] }} />
          </TouchableOpacity>
        </View>

        <ScrollView showsVerticalScrollIndicator={false}>
          <View style={styles.detailContent}>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Status</Text>
              <View style={[styles.statusBadge, { backgroundColor: selectedIssueDetail.status === 'Resolved' ? COLORS.primary + '15' : COLORS.danger + '15' }]}>
                <Text style={[styles.statusBadgeText, { color: selectedIssueDetail.status === 'Resolved' ? COLORS.primary : COLORS.danger }]}>
                  {selectedIssueDetail.status}
                </Text>
              </View>
            </View>

            <View style={styles.detailItem}>
              <Text style={styles.detailLabel}>Resource & Type</Text>
              <Text style={styles.detailValue}>{selectedIssueDetail.issue_type}</Text>
            </View>

            <View style={styles.detailItem}>
              <Text style={styles.detailLabel}>Location</Text>
              <Text style={styles.detailValue}>{selectedIssueDetail.location || selectedIssueDetail.locality}</Text>
            </View>

            {selectedIssueDetail.landmark && (
              <View style={styles.detailItem}>
                <Text style={styles.detailLabel}>Landmark</Text>
                <Text style={styles.detailValue}>{selectedIssueDetail.landmark}</Text>
              </View>
            )}

            <View style={styles.detailItem}>
              <Text style={styles.detailLabel}>Reported On</Text>
              <Text style={styles.detailValue}>{new Date(selectedIssueDetail.timestamp).toLocaleString()}</Text>
            </View>

            {selectedIssueDetail.resolved_at && (
              <View style={styles.detailItem}>
                <Text style={styles.detailLabel}>Resolved On</Text>
                <Text style={styles.detailValue}>{new Date(selectedIssueDetail.resolved_at).toLocaleString()}</Text>
              </View>
            )}
          </View>

          <TouchableOpacity style={styles.closeDetailBtn} onPress={() => setSelectedIssueDetail(null)}>
            <Text style={styles.buttonText}>Close</Text>
          </TouchableOpacity>
        </ScrollView>
      </Animated.View>
    </View>
  );

  const BottomNav = () => (
    <View style={styles.bottomNav}>
      <TouchableOpacity style={styles.navItem} onPress={() => setScreen('home')}>
        <Home color={screen === 'home' ? COLORS.primary : COLORS.textSecondary} size={24} />
        <Text style={[styles.navText, screen === 'home' && { color: COLORS.primary }]}>Home</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.navItem} onPress={() => setScreen('report')}>
        <View style={styles.reportFab}>
          <Plus color="#fff" size={28} />
        </View>
      </TouchableOpacity>
      <TouchableOpacity style={styles.navItem} onPress={() => setScreen('history')}>
        <History color={screen === 'history' ? COLORS.primary : COLORS.textSecondary} size={24} />
        <Text style={[styles.navText, screen === 'history' && { color: COLORS.primary }]}>Reports</Text>
      </TouchableOpacity>
    </View>
  );

  const renderHome = () => (
    <View style={styles.mainContent}>
      <Header title="Eco-Track" />
      <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        <View style={styles.heroSection}>
          <Text style={styles.greeting}>Good Afternoon,</Text>
          <Text style={styles.userName}>{currentUser.name}</Text>
        </View>

        <View style={styles.scoreCard}>
          <View style={styles.scoreTop}>
            <Text style={styles.scoreArea}>Weekly Activity</Text>
            <BarChart3 color={COLORS.primary} size={20} />
          </View>
          <View style={styles.graphContainer}>
            {historicalData.map((day, i) => {
              const maxVal = Math.max(...historicalData.map(d => d.value), 5);
              const heightPerc = (day.value / maxVal) * 100;
              return (
                <View key={i} style={styles.graphBarColumn}>
                  <View style={styles.graphBarBg}>
                    <View style={[styles.graphBarFill, { height: `${heightPerc}%` }]} />
                  </View>
                  <Text style={styles.graphBarLabel}>{day.name}</Text>
                </View>
              );
            })}
          </View>
          <Text style={styles.scoreDesc}>System-wide reports (Last 7 days)</Text>
        </View>

        <View style={styles.menuGrid}>
          {[
            { label: '📊 Report Issue', screen: 'report', icon: AlertCircle, color: COLORS.danger },
            { label: '📋 All Reports', screen: 'history', icon: History, color: COLORS.accent },
          ].map((item, idx) => (
            <TouchableOpacity key={idx} style={styles.menuItem} onPress={() => setScreen(item.screen)}>
              <View style={[styles.menuIconBox, { backgroundColor: item.color + '15' }]}>
                <item.icon color={item.color} size={24} />
              </View>
              <Text style={styles.menuLabel}>{item.label}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Droplets color={COLORS.accent} size={20} />
            <Text style={styles.statValue}>{areaStats?.impact || 0}L</Text>
            <Text style={styles.statLabel}>Water Saved</Text>
          </View>
          <View style={styles.statBox}>
            <CheckCircle2 color={COLORS.primary} size={20} />
            <Text style={styles.statValue}>{areaStats?.resolved || 0}</Text>
            <Text style={styles.statLabel}>Issues Fixed</Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );

  const renderReport = () => (
    <View style={styles.mainContent}>
      <View style={styles.stepHeader}>
        <TouchableOpacity onPress={() => {
          if (reportStep === 'category') setScreen('home');
          else if (reportStep === 'issue') setReportStep('category');
          else if (reportStep === 'pincode') setReportStep('issue');
          else if (reportStep === 'locality') setReportStep('pincode');
          else if (reportStep === 'landmark') setReportStep('locality');
          else if (reportStep === 'confirm') setReportStep('landmark');
        }}>
          <ChevronLeft color={COLORS.text} size={24} />
        </TouchableOpacity>
        <Text style={styles.headerTitleText}>Report Issue</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.scrollContainer} contentContainerStyle={{ paddingBottom: 100 }}>
        {reportStep === 'category' && (
          <View style={styles.stepContent}>
            <Text style={styles.stepTitle}>Select Resource</Text>
            {RESOURCES.map(item => (
              <TouchableOpacity 
                key={item.key} 
                style={[styles.typeCard, selectedCategory?.key === item.key && styles.selectedTypeCard]}
                onPress={() => setSelectedCategory(item)}
              >
                <View style={[styles.typeIcon, { backgroundColor: item.color + '20' }]}>
                  <item.icon color={item.color} size={24} />
                </View>
                <Text style={styles.typeLabel}>{item.label}</Text>
                {selectedCategory?.key === item.key && <CheckCircle2 color={item.color} size={20} />}
              </TouchableOpacity>
            ))}
          </View>
        )}

        {reportStep === 'issue' && (
          <View style={styles.stepContent}>
            <Text style={styles.stepTitle}>Select Issue Type</Text>
            {ISSUE_OPTIONS[selectedCategory?.key]?.map((item, idx) => (
              <TouchableOpacity 
                key={idx} 
                style={[styles.typeCard, selectedIssue === item && styles.selectedTypeCard]}
                onPress={() => setSelectedIssue(item)}
              >
                <Text style={styles.typeLabel}>{item}</Text>
                {selectedIssue === item && <CheckCircle2 color={selectedCategory.color} size={20} />}
              </TouchableOpacity>
            ))}
          </View>
        )}

        {reportStep === 'pincode' && (
          <View style={styles.stepContent}>
            <Text style={styles.stepTitle}>Enter Pincode</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. 560038"
              placeholderTextColor={COLORS.textSecondary}
              keyboardType="numeric"
              maxLength={6}
              value={pincode}
              onChangeText={setPincode}
            />
          </View>
        )}

        {reportStep === 'locality' && (
          <View style={styles.stepContent}>
            <Text style={styles.stepTitle}>Select Locality</Text>
            {localities.map((item, idx) => (
              <TouchableOpacity 
                key={idx} 
                style={[styles.localityItem, selectedLocality?.Name === item.Name && styles.selectedLocality]}
                onPress={() => setSelectedLocality(item)}
              >
                <MapPin color={selectedLocality?.Name === item.Name ? COLORS.primary : COLORS.textSecondary} size={18} />
                <Text style={[styles.localityText, selectedLocality?.Name === item.Name && { color: COLORS.primary }]}>{item.Name}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {reportStep === 'landmark' && (
          <View style={styles.stepContent}>
            <Text style={styles.stepTitle}>Enter Landmark</Text>
            <TextInput
              style={[styles.input, { height: 100, textAlignVertical: 'top' }]}
              placeholder="e.g. Opp. Metro Pillar 120"
              placeholderTextColor={COLORS.textSecondary}
              multiline
              value={landmark}
              onChangeText={setLandmark}
            />
          </View>
        )}

        {reportStep === 'confirm' && (
          <View style={styles.stepContent}>
            <Text style={styles.stepTitle}>Confirm Details</Text>
            <View style={styles.summaryCard}>
              <View style={styles.summaryItem}>
                <Text style={styles.summaryLabel}>Category</Text>
                <Text style={styles.summaryValue}>{selectedCategory?.label}</Text>
              </View>
              <View style={styles.summaryItem}>
                <Text style={styles.summaryLabel}>Issue</Text>
                <Text style={styles.summaryValue}>{selectedIssue}</Text>
              </View>
              <View style={styles.summaryItem}>
                <Text style={styles.summaryLabel}>Location</Text>
                <Text style={styles.summaryValue}>{selectedLocality?.Name}</Text>
              </View>
              <View style={styles.summaryItem}>
                <Text style={styles.summaryLabel}>Landmark</Text>
                <Text style={styles.summaryValue}>{landmark}</Text>
              </View>
            </View>
          </View>
        )}
      </ScrollView>

      {/* STICKY FOOTER BUTTON */}
      <View style={styles.stickyFooter}>
        {reportStep === 'pincode' ? (
          <TouchableOpacity 
            style={[styles.primaryButton, pincode.length !== 6 && { opacity: 0.5 }]} 
            onPress={handlePincodeSubmit}
            disabled={pincode.length !== 6 || loading}
          >
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Lookup Locality</Text>}
          </TouchableOpacity>
        ) : (
          <TouchableOpacity 
            style={[
              styles.primaryButton, 
              ((!selectedCategory && reportStep === 'category') || 
               (!selectedIssue && reportStep === 'issue') || 
               (!selectedLocality && reportStep === 'locality') || 
               (!landmark && reportStep === 'landmark')) && { opacity: 0.5 }
            ]}
            onPress={() => {
              if (reportStep === 'category') setReportStep('issue');
              else if (reportStep === 'issue') setReportStep('pincode');
              else if (reportStep === 'locality') setReportStep('landmark');
              else if (reportStep === 'landmark') setReportStep('confirm');
              else if (reportStep === 'confirm') submitReport();
            }}
            disabled={
              loading ||
              (!selectedCategory && reportStep === 'category') || 
              (!selectedIssue && reportStep === 'issue') || 
              (!selectedLocality && reportStep === 'locality') || 
              (!landmark && reportStep === 'landmark')
            }
          >
            {loading ? <ActivityIndicator color="#fff" /> : (
              <Text style={styles.buttonText}>
                {reportStep === 'confirm' ? '✅ Yes, Submit' : 'Continue'}
              </Text>
            )}
          </TouchableOpacity>
        )}
      </View>
    </View>
  );

  const renderSuccess = () => (
    <View style={styles.successOverlay}>
      <Animated.View style={[
        styles.successCard,
        {
          transform: [
            { scale: successAnim },
            { translateY: successAnim.interpolate({ inputRange: [0, 1], outputRange: [100, 0] }) }
          ],
          opacity: successAnim
        }
      ]}>
        <View style={styles.successIconBox}>
          <CheckCircle2 color="#fff" size={64} />
        </View>
        <Text style={styles.successTitle}>Report Submitted!</Text>
        <Text style={styles.successSubtitle}>Thank you for being a responsible citizen. We are on it!</Text>
        <View style={styles.impactBadge}>
          <Shield color={COLORS.primary} size={16} />
          <Text style={styles.impactBadgeText}>+200 Impact Points</Text>
        </View>
      </Animated.View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      {screen === 'home' && renderHome()}
      {screen === 'report' && renderReport()}
      {screen === 'success' && renderSuccess()}
      {screen === 'history' && renderHistory()}
      
      {selectedIssueDetail && renderIssueDetail()}
      
      {(screen === 'home' || screen === 'history') && <BottomNav />}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    paddingTop: Platform.OS === 'android' ? 30 : 0,
  },
  mainContent: {
    flex: 1,
  },
  scrollContainer: {
    padding: 20,
    flex: 1,
  },
  appHeader: {
    height: 60,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    backgroundColor: COLORS.header,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.cardBorder,
  },
  headerTitleText: {
    color: COLORS.text,
    fontSize: 18,
    fontWeight: 'bold',
  },
  heroSection: {
    marginVertical: 20,
  },
  greeting: {
    color: COLORS.textSecondary,
    fontSize: 16,
  },
  userName: {
    color: COLORS.text,
    fontSize: 28,
    fontWeight: 'bold',
  },
  scoreCard: {
    backgroundColor: COLORS.card,
    borderRadius: 24,
    padding: 24,
    borderWidth: 1,
    borderColor: COLORS.cardBorder,
    marginBottom: 24,
  },
  scoreTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  scoreArea: {
    color: COLORS.textSecondary,
    fontSize: 14,
    fontWeight: 'bold',
  },
  scoreBig: {
    color: COLORS.text,
    fontSize: 48,
    fontWeight: 'bold',
  },
  scoreDesc: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  scoreBarContainer: {
    height: 6,
    backgroundColor: COLORS.background,
    borderRadius: 3,
  },
  graphContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    height: 120,
    marginVertical: 20,
  },
  graphBarColumn: {
    alignItems: 'center',
    width: (width - 120) / 7,
  },
  graphBarBg: {
    width: 6,
    height: 80,
    backgroundColor: COLORS.background,
    borderRadius: 3,
    justifyContent: 'flex-end',
  },
  graphBarFill: {
    width: '100%',
    backgroundColor: COLORS.primary,
    borderRadius: 3,
  },
  graphBarLabel: {
    color: COLORS.textSecondary,
    fontSize: 10,
    marginTop: 8,
    fontWeight: 'bold',
  },
  menuGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 24,
  },
  menuItem: {
    width: (width - 52) / 2,
    backgroundColor: COLORS.card,
    borderRadius: 20,
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.cardBorder,
    alignItems: 'center',
  },
  menuIconBox: {
    width: 48,
    height: 48,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
  },
  menuLabel: {
    color: COLORS.text,
    fontSize: 13,
    fontWeight: 'bold',
  },
  statsRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 100, // Space for bottom nav
  },
  statBox: {
    flex: 1,
    backgroundColor: COLORS.card,
    borderRadius: 20,
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.cardBorder,
  },
  statValue: {
    color: COLORS.text,
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 8,
  },
  statLabel: {
    color: COLORS.textSecondary,
    fontSize: 12,
  },
  bottomNav: {
    height: 70,
    backgroundColor: COLORS.header,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    borderTopWidth: 1,
    borderTopColor: COLORS.cardBorder,
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingBottom: 10,
  },
  navItem: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  navText: {
    fontSize: 10,
    color: COLORS.textSecondary,
    marginTop: 4,
  },
  reportFab: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: COLORS.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: -40,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 5,
  },
  stepHeader: {
    height: 60,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.cardBorder,
  },
  stepContent: {
    paddingVertical: 20,
  },
  stepTitle: {
    color: COLORS.text,
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  typeCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 18,
    backgroundColor: COLORS.card,
    borderRadius: 18,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedTypeCard: {
    borderColor: COLORS.primary,
    backgroundColor: COLORS.primary + '10',
  },
  typeIcon: {
    width: 44,
    height: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  typeLabel: {
    color: COLORS.text,
    fontSize: 16,
    fontWeight: '600',
    flex: 1,
  },
  input: {
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 18,
    color: COLORS.text,
    fontSize: 16,
    borderWidth: 1,
    borderColor: COLORS.cardBorder,
    marginBottom: 20,
  },
  localityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 18,
    backgroundColor: COLORS.card,
    borderRadius: 16,
    marginBottom: 10,
    gap: 12,
    borderWidth: 1,
    borderColor: COLORS.cardBorder,
  },
  selectedLocality: {
    borderColor: COLORS.primary,
    backgroundColor: COLORS.primary + '10',
  },
  localityText: {
    color: COLORS.text,
    fontSize: 15,
  },
  primaryButton: {
    backgroundColor: COLORS.primary,
    padding: 18,
    borderRadius: 16,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  summaryCard: {
    backgroundColor: COLORS.card,
    padding: 20,
    borderRadius: 18,
    marginBottom: 20,
    gap: 10,
  },
  summaryLabel: {
    color: COLORS.textSecondary,
    fontSize: 14,
  },
  summaryValue: {
    color: COLORS.text,
    fontWeight: 'bold',
  },
  stickyFooter: {
    padding: 20,
    backgroundColor: COLORS.background,
    borderTopWidth: 1,
    borderTopColor: COLORS.cardBorder,
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
  },
  successOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(15, 23, 42, 0.9)',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  successCard: {
    width: width * 0.85,
    backgroundColor: COLORS.card,
    borderRadius: 32,
    padding: 40,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.cardBorder,
  },
  successIconBox: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: COLORS.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 10,
  },
  successTitle: {
    color: COLORS.text,
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  successSubtitle: {
    color: COLORS.textSecondary,
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 24,
  },
  impactBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.primary + '20',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 8,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 60,
  },
  emptyText: {
    color: COLORS.textSecondary,
    fontSize: 16,
    marginTop: 16,
  },
  issueListItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.card,
    borderRadius: 20,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.cardBorder,
  },
  statusIndicator: {
    width: 4,
    height: 40,
    borderRadius: 2,
    marginRight: 16,
  },
  issueListInfo: {
    flex: 1,
  },
  issueListType: {
    color: COLORS.text,
    fontSize: 16,
    fontWeight: 'bold',
  },
  issueListLoc: {
    color: COLORS.textSecondary,
    fontSize: 13,
    marginTop: 2,
  },
  issueListTime: {
    color: COLORS.textSecondary,
    fontSize: 11,
    marginTop: 4,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
    marginRight: 12,
  },
  statusBadgeText: {
    fontSize: 11,
    fontWeight: 'bold',
  },
  detailOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(15, 23, 42, 0.8)',
    justifyContent: 'flex-end',
    zIndex: 2000,
  },
  detailCard: {
    backgroundColor: COLORS.card,
    borderTopLeftRadius: 32,
    borderTopRightRadius: 32,
    padding: 24,
    paddingBottom: 40,
    borderTopWidth: 1,
    borderTopColor: COLORS.cardBorder,
  },
  detailHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  detailTitle: {
    color: COLORS.text,
    fontSize: 20,
    fontWeight: 'bold',
  },
  detailContent: {
    gap: 20,
    marginBottom: 30,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  detailItem: {
    gap: 4,
  },
  detailLabel: {
    color: COLORS.textSecondary,
    fontSize: 13,
  },
  detailValue: {
    color: COLORS.text,
    fontSize: 16,
    fontWeight: '500',
  },
  closeDetailBtn: {
    backgroundColor: COLORS.cardBorder,
    padding: 18,
    borderRadius: 16,
    alignItems: 'center',
  }
});
