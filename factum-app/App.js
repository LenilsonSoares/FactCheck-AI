import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  SafeAreaView,
  Animated,
  StatusBar,
  ActivityIndicator,
  Dimensions,
  Image,
  Alert,
  Share,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { Feather, MaterialIcons, FontAwesome5 } from '@expo/vector-icons';

const { width, height } = Dimensions.get('window');

const App = () => {
  const [showSplash, setShowSplash] = useState(true);
  const [inputText, setInputText] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [result, setResult] = useState(null);
  const [recentItems, setRecentItems] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState(true);
  
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const loadingWidth = useRef(new Animated.Value(0)).current;
  const resultAnim = useRef(new Animated.Value(0)).current;

  const [apiConfig, setApiConfig] = useState({
    baseUrl: 'http://192.168.1.100:5000', // ALTERE PARA O IP DO SEU BACKEND
    timeout: 30000,
  });

  useEffect(() => {
    loadConfig();
    loadRecentVerifications();
    checkConnectivity();
    
    Animated.timing(loadingWidth, {
      toValue: 100,
      duration: 2800,
      useNativeDriver: false,
    }).start();

    const timer = setTimeout(() => {
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 450,
        useNativeDriver: true,
      }).start();
      setShowSplash(false);
    }, 2800);

    const unsubscribe = NetInfo.addEventListener(state => {
      setConnectionStatus(state.isConnected);
    });

    return () => {
      clearTimeout(timer);
      unsubscribe();
    };
  }, []);

  const loadConfig = async () => {
    try {
      const savedConfig = await AsyncStorage.getItem('api_config');
      if (savedConfig) {
        const config = JSON.parse(savedConfig);
        setApiConfig(config);
      }
    } catch (error) {
      console.error('Erro ao carregar config:', error);
    }
  };

  const checkConnectivity = async () => {
    try {
      const response = await fetch(`${apiConfig.baseUrl}/health`, {
        method: 'GET',
        timeout: 5000,
      });
      if (!response.ok) throw new Error('Backend offline');
    } catch (error) {
      console.log('Backend não disponível');
    }
  };

  const loadRecentVerifications = async () => {
    try {
      const saved = await AsyncStorage.getItem('verification_history');
      if (saved) {
        const history = JSON.parse(saved);
        setRecentItems(history.slice(0, 5));
      }
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
    }
  };

  const saveToHistory = async (verification) => {
    try {
      const saved = await AsyncStorage.getItem('verification_history');
      let history = saved ? JSON.parse(saved) : [];
      history = [verification, ...history];
      if (history.length > 50) history = history.slice(0, 50);
      await AsyncStorage.setItem('verification_history', JSON.stringify(history));
      setRecentItems(history.slice(0, 5));
    } catch (error) {
      console.error('Erro ao salvar histórico:', error);
    }
  };

  const shareResult = async () => {
    try {
      await Share.share({
        message: `Factum - Verificação de Fatos\n\nAfirmação: "${result.text}"\nStatus: ${result.status}\nConfiança: ${result.confidence}%\n\n${result.details}`,
        title: 'Resultado da Verificação',
      });
    } catch (error) {
      console.error('Erro ao compartilhar:', error);
    }
  };

  const handleVerify = async () => {
    if (!inputText.trim()) {
      Alert.alert('Atenção', 'Por favor, digite uma afirmação para verificar');
      return;
    }

    if (!connectionStatus) {
      Alert.alert('Sem conexão', 'Verifique sua internet e tente novamente');
      return;
    }

    setIsVerifying(true);
    setResult(null);
    resultAnim.setValue(0);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), apiConfig.timeout);

      const response = await fetch(`${apiConfig.baseUrl}/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          text: inputText.trim(),
          timestamp: new Date().toISOString(),
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Erro na comunicação com o servidor');
      }

      const data = await response.json();
      
      const verificationResult = {
        id: Date.now().toString(),
        text: inputText.trim(),
        status: data.status,
        color: getStatusColor(data.status),
        bg: getStatusBgColor(data.status),
        confidence: data.confidence,
        details: data.details,
        sources: data.sources || [],
        source_type: data.source_type,
        timestamp: new Date().toISOString(),
      };

      setResult(verificationResult);
      await saveToHistory(verificationResult);
      
      Animated.spring(resultAnim, {
        toValue: 1,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }).start();
      
    } catch (error) {
      console.error('Erro na verificação:', error);
      
      if (error.name === 'AbortError') {
        Alert.alert('Timeout', 'O servidor demorou muito para responder. Tente novamente.');
      } else {
        Alert.alert(
          'Erro de Conexão',
          `Não foi possível conectar ao servidor.\n\nVerifique se o backend está rodando em:\n${apiConfig.baseUrl}`
        );
      }
    } finally {
      setIsVerifying(false);
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'VERDADEIRO': return '#22c55e';
      case 'FALSO': return '#ef4444';
      case 'IMPRECISO': return '#eab308';
      default: return '#94a3b8';
    }
  };

  const getStatusBgColor = (status) => {
    switch(status) {
      case 'VERDADEIRO': return 'rgba(34,197,94,0.15)';
      case 'FALSO': return 'rgba(239,68,68,0.15)';
      case 'IMPRECISO': return 'rgba(234,179,8,0.15)';
      default: return 'rgba(148,163,184,0.15)';
    }
  };

  const showExamples = () => {
    const examplesList = [
      'As urnas eletrônicas brasileiras são seguras?',
      'Lula foi preso pela Lava Jato?',
      'Bolsonaro privatizou os Correios?',
      'O voto no Brasil é obrigatório?',
      'A urna eletrônica já foi hackeada?',
      'Eleições no Brasil têm fraude comprovada?',
    ];
    
    Alert.alert(
      'Exemplos de Verificação',
      'Escolha um exemplo para testar:',
      examplesList.map(ex => ({
        text: ex,
        onPress: () => setInputText(ex),
      }))
    );
  };

  const clearResult = () => {
    setResult(null);
    setInputText('');
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'VERDADEIRO': 
        return <Feather name="check-circle" size={14} color="#22c55e" />;
      case 'FALSO': 
        return <Feather name="x-circle" size={14} color="#ef4444" />;
      case 'IMPRECISO': 
        return <Feather name="alert-triangle" size={14} color="#eab308" />;
      default: 
        return <Feather name="help-circle" size={14} color="#94a3b8" />;
    }
  };

  if (showSplash) {
    return (
      <LinearGradient
        colors={['#0a1628', '#020617']}
        style={styles.splashContainer}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <StatusBar barStyle="light-content" backgroundColor="#050810" />
        <View style={styles.splashContent}>
          <View style={styles.logoContainer}>
            <Image
              source={require('./assets/factum.png')}
              style={styles.splashLogo}
              resizeMode="contain"
            />
          </View>
          <Text style={styles.splashTagline}>A verdade por trás da informação.</Text>
          <View style={styles.loadingContainer}>
            <View style={styles.loadingBar}>
              <Animated.View 
                style={[
                  styles.loadingFill,
                  {
                    width: loadingWidth.interpolate({
                      inputRange: [0, 100],
                      outputRange: ['0%', '100%']
                    })
                  }
                ]} 
              />
            </View>
            <Text style={styles.loadingText}>Carregando experiência Factum...</Text>
          </View>
        </View>
      </LinearGradient>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#050810" />
      
      <Animated.View style={[styles.mainContainer, { opacity: fadeAnim }]}>
        <View style={styles.header}>
          <View style={styles.headerLogoContainer}>
            <Image
              source={require('./assets/factum.png')}
              style={styles.headerLogo}
              resizeMode="contain"
            />
          </View>
          {!connectionStatus && (
            <View style={styles.offlineBadge}>
              <Feather name="wifi-off" size={14} color="#ef4444" />
              <Text style={styles.offlineText}>Offline</Text>
            </View>
          )}
        </View>
        
        <Text style={styles.tagline}>A verdade por trás da informação.</Text>

        <ScrollView 
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.scrollContent}
        >
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Verifique uma informação</Text>
            <Text style={styles.cardSubtitle}>
              Digite uma afirmação, notícia ou cole um link para analisarmos com IA.
            </Text>
            
            <TextInput
              style={styles.textInput}
              multiline
              numberOfLines={3}
              placeholder="Ex: As urnas eletrônicas não são seguras."
              placeholderTextColor="#6b7b9b"
              value={inputText}
              onChangeText={setInputText}
              editable={!isVerifying}
            />
            
            <TouchableOpacity 
              style={[styles.verifyButton, isVerifying && styles.verifyButtonDisabled]}
              onPress={handleVerify}
              disabled={isVerifying}
            >
              {isVerifying ? (
                <ActivityIndicator color="#fff" size="small" />
              ) : (
                <>
                  <Feather name="shield" size={18} color="#fff" />
                  <Text style={styles.verifyButtonText}>Verificar</Text>
                </>
              )}
            </TouchableOpacity>

            {result && (
              <Animated.View 
                style={[
                  styles.resultContainer,
                  {
                    transform: [{
                      translateY: resultAnim.interpolate({
                        inputRange: [0, 1],
                        outputRange: [20, 0]
                      })
                    }],
                    opacity: resultAnim
                  }
                ]}
              >
                <View style={styles.resultHeader}>
                  <View style={styles.resultLabelContainer}>
                    <FontAwesome5 name="robot" size={14} color="#8b9bb5" />
                    <Text style={styles.resultLabel}> Análise Factum</Text>
                  </View>
                  <View style={[styles.statusPill, { backgroundColor: result.bg }]}>
                    {getStatusIcon(result.status)}
                    <Text style={[styles.statusText, { color: result.color }]}>
                      {result.status}
                    </Text>
                  </View>
                </View>
                
                <Text style={styles.resultQuote}>
                  "{result.text.substring(0, 120)}"
                </Text>
                
                <View style={styles.confidenceContainer}>
                  <View style={styles.confidenceBarBg}>
                    <View 
                      style={[
                        styles.confidenceBarFill, 
                        { width: `${result.confidence}%`, backgroundColor: result.color }
                      ]} 
                    />
                  </View>
                  <View style={styles.confidenceLabels}>
                    <Text style={styles.confidenceLabel}>confiabilidade</Text>
                    <Text style={[styles.confidenceValue, { color: result.color }]}>
                      {result.confidence}%
                    </Text>
                  </View>
                </View>
                
                <View style={styles.detailsContainer}>
                  <Feather name="info" size={14} color="#8ba0c0" />
                  <Text style={styles.detailsText}> {result.details}</Text>
                </View>

                {result.source_type && (
                  <View style={styles.sourceTypeContainer}>
                    <MaterialIcons name="source" size={12} color="#64748b" />
                    <Text style={styles.sourceTypeText}>
                      Fonte: {result.source_type === 'api' ? 'Google Fact Check API' : 'Modelo de IA'}
                    </Text>
                  </View>
                )}

                <View style={styles.resultActions}>
                  <TouchableOpacity onPress={shareResult} style={styles.shareButton}>
                    <Feather name="share-2" size={16} color="#94a3b8" />
                    <Text style={styles.shareButtonText}>Compartilhar</Text>
                  </TouchableOpacity>
                  <TouchableOpacity onPress={clearResult} style={styles.clearResultButton}>
                    <Feather name="x" size={16} color="#94a3b8" />
                    <Text style={styles.clearResultButtonText}>Limpar</Text>
                  </TouchableOpacity>
                </View>
              </Animated.View>
            )}
          </View>

          <View style={styles.quickActions}>
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={() => Alert.alert('Colar Link', 'Função disponível em breve')}
            >
              <Feather name="link" size={16} color="#b9c3dd" />
              <Text style={styles.actionButtonText}>Colar link</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={showExamples}
            >
              <Feather name="help-circle" size={16} color="#b9c3dd" />
              <Text style={styles.actionButtonText}>Exemplos</Text>
            </TouchableOpacity>
          </View>

          {recentItems.length > 0 && (
            <View style={styles.recentSection}>
              <View style={styles.recentHeader}>
                <Feather name="clock" size={16} color="#a0b0cc" />
                <Text style={styles.recentTitle}>Verificações recentes</Text>
              </View>
              {recentItems.map((item, index) => (
                <TouchableOpacity 
                  key={index} 
                  style={styles.recentCard}
                  onPress={() => {
                    setInputText(item.text.replace(/"/g, ''));
                    setResult(null);
                  }}
                >
                  <Text style={styles.recentText}>{item.text}</Text>
                  <View style={styles.recentFooter}>
                    <View style={[styles.recentStatus, { backgroundColor: item.bg }]}>
                      {getStatusIcon(item.status)}
                      <Text style={[styles.recentStatusText, { color: item.color }]}>
                        {item.status}
                      </Text>
                    </View>
                    <Text style={styles.recentConfidence}>{item.confidence}% confiança</Text>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </ScrollView>
      </Animated.View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050810',
  },
  splashContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  splashContent: {
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
  },
  logoContainer: {
    width: width * 0.85,
    maxWidth: 380,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  splashLogo: {
    width: '100%',
    height: undefined,
    aspectRatio: 1,
  },
  splashTagline: {
    color: '#cbd5e1',
    fontSize: 16,
    fontWeight: '500',
    marginTop: 24,
  },
  loadingContainer: {
    position: 'absolute',
    bottom: 70,
    width: 220,
    alignItems: 'center',
    gap: 12,
  },
  loadingBar: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 40,
    overflow: 'hidden',
    height: 4,
    width: '100%',
  },
  loadingFill: {
    height: '100%',
    backgroundColor: '#3b82f6',
    borderRadius: 40,
  },
  loadingText: {
    color: '#5b6e8c',
    fontSize: 12,
    fontWeight: '500',
  },
  mainContainer: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 8,
    position: 'relative',
  },
  headerLogoContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerLogo: {
    width: 150,
    height: 60,
  },
  offlineBadge: {
    position: 'absolute',
    right: 20,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(239,68,68,0.15)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 20,
    gap: 4,
  },
  offlineText: {
    color: '#ef4444',
    fontSize: 10,
    fontWeight: '600',
  },
  tagline: {
    textAlign: 'center',
    color: '#6b7b9b',
    fontSize: 13,
    marginBottom: 20,
    fontWeight: '500',
  },
  scrollContent: {
    paddingBottom: 40,
  },
  card: {
    marginHorizontal: 18,
    backgroundColor: 'rgba(17,24,39,0.8)',
    borderRadius: 28,
    padding: 22,
    borderWidth: 1,
    borderColor: '#2d3a5e',
  },
  cardTitle: {
    color: 'white',
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 6,
  },
  cardSubtitle: {
    color: '#8b9bb5',
    fontSize: 13,
    marginBottom: 18,
    lineHeight: 19,
  },
  textInput: {
    backgroundColor: '#0a0e1a',
    borderWidth: 1,
    borderColor: '#253153',
    borderRadius: 20,
    padding: 14,
    color: 'white',
    fontSize: 15,
    textAlignVertical: 'top',
    minHeight: 100,
  },
  verifyButton: {
    backgroundColor: '#2563eb',
    borderRadius: 40,
    padding: 14,
    alignItems: 'center',
    marginTop: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
  },
  verifyButtonDisabled: {
    opacity: 0.8,
  },
  verifyButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  resultContainer: {
    marginTop: 20,
    padding: 16,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: '#2d3a5e',
    backgroundColor: '#0f1422',
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  resultLabelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  resultLabel: {
    color: '#8b9bb5',
    fontSize: 12,
    fontWeight: '700',
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 100,
    gap: 4,
  },
  statusText: {
    fontSize: 11,
    fontWeight: '700',
  },
  resultQuote: {
    color: '#e2e8f0',
    fontSize: 14,
    marginBottom: 12,
    lineHeight: 20,
    borderLeftWidth: 3,
    borderLeftColor: '#3b82f6',
    paddingLeft: 12,
  },
  confidenceContainer: {
    marginVertical: 8,
  },
  confidenceBarBg: {
    backgroundColor: '#1e293b',
    borderRadius: 40,
    height: 8,
    overflow: 'hidden',
  },
  confidenceBarFill: {
    height: '100%',
    borderRadius: 40,
  },
  confidenceLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  confidenceLabel: {
    color: '#64748b',
    fontSize: 12,
  },
  confidenceValue: {
    fontSize: 13,
    fontWeight: '700',
  },
  detailsContainer: {
    marginTop: 12,
    backgroundColor: 'rgba(0,0,0,0.3)',
    padding: 12,
    borderRadius: 18,
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  detailsText: {
    color: '#8ba0c0',
    fontSize: 12,
    flex: 1,
  },
  sourceTypeContainer: {
    marginTop: 10,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  sourceTypeText: {
    color: '#64748b',
    fontSize: 10,
  },
  resultActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 16,
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#1e293b',
  },
  shareButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  shareButtonText: {
    color: '#94a3b8',
    fontSize: 12,
  },
  clearResultButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  clearResultButtonText: {
    color: '#94a3b8',
    fontSize: 12,
  },
  quickActions: {
    flexDirection: 'row',
    gap: 12,
    marginHorizontal: 18,
    marginTop: 20,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    padding: 12,
    backgroundColor: '#0f172f',
    borderWidth: 1,
    borderColor: '#253153',
    borderRadius: 40,
  },
  actionButtonText: {
    color: '#b9c3dd',
    fontSize: 13,
    fontWeight: '500',
  },
  recentSection: {
    marginHorizontal: 18,
    marginTop: 28,
    marginBottom: 40,
  },
  recentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 14,
  },
  recentTitle: {
    color: '#a0b0cc',
    fontSize: 13,
    fontWeight: '700',
  },
  recentCard: {
    backgroundColor: '#111827',
    borderWidth: 1,
    borderColor: '#253153',
    borderRadius: 20,
    padding: 14,
    marginBottom: 12,
  },
  recentText: {
    color: '#e2e8f0',
    fontSize: 14,
    marginBottom: 10,
    fontWeight: '500',
  },
  recentFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  recentStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 100,
    gap: 4,
  },
  recentStatusText: {
    fontSize: 11,
    fontWeight: '700',
  },
  recentConfidence: {
    color: '#7f8eaa',
    fontSize: 12,
    fontWeight: '500',
  },
});

export default App;