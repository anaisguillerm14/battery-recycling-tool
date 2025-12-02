import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  LineChart,
  Line,
  ReferenceLine
} from 'recharts';
import { 
  Settings, 
  Factory, 
  TrendingUp, 
  Truck, 
  Zap, 
  AlertTriangle, 
  Info,
  Euro,
  Save,
  RotateCcw,
  FileText
} from 'lucide-react';

// --- Composants UI ---
const Card = ({ children, className = "" }) => (
  <div className={`bg-white rounded-xl shadow-sm border border-slate-200 ${className}`}>
    {children}
  </div>
);

const SectionHeader = ({ icon: Icon, title }) => (
  <div className="flex items-center gap-2 mb-4 text-slate-800 border-b pb-2 border-slate-100">
    <Icon className="w-5 h-5 text-blue-600" />
    <h3 className="font-bold text-lg">{title}</h3>
  </div>
);

const InputGroup = ({ label, value, onChange, unit, min, max, step = 1, help }) => (
  <div className="mb-4">
    <div className="flex justify-between mb-1">
      <label className="text-sm font-medium text-slate-700 flex items-center gap-1">
        {label}
        {help && <span className="text-slate-400 cursor-help" title={help}><Info className="w-3 h-3" /></span>}
      </label>
      <span className="text-sm font-bold text-blue-600">{typeof value === 'number' ? value.toLocaleString() : value} {unit}</span>
    </div>
    <input 
      type="range" 
      min={min} 
      max={max} 
      step={step}
      value={value} 
      onChange={(e) => onChange(parseFloat(e.target.value))}
      className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
    />
  </div>
);

const KpiCard = ({ title, value, subtext, trend, color = "blue" }) => {
  const colorClasses = {
    blue: "bg-blue-50 text-blue-700 border-blue-100",
    green: "bg-emerald-50 text-emerald-700 border-emerald-100",
    amber: "bg-amber-50 text-amber-700 border-amber-100",
    red: "bg-red-50 text-red-700 border-red-100",
  };
  
  return (
    <div className={`p-4 rounded-xl border ${colorClasses[color]} flex flex-col justify-between`}>
      <span className="text-xs font-semibold uppercase tracking-wider opacity-80">{title}</span>
      <div className="mt-2">
        <span className="text-2xl font-bold">{value}</span>
      </div>
      {subtext && <span className="text-xs opacity-70 mt-1">{subtext}</span>}
    </div>
  );
};

export default function BatteryRecyclingSimulator() {
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // --- ÉTATS & PARAMÈTRES ---
  
  // 1. Scénarios Prédéfinis
  const scenarios = {
    pessimiste: {
      blackMassVolume: 15000,
      shareNMC: 60,
      metalPrices: 0.8, // facteur par rapport à la base
      energyCostEU: 180, // €/MWh
      logisticsCost: 120, // €/tonne
      yieldRecovery: 85,
      pcamPremium: 2 // €/kg premium Made in EU
    },
    conservateur: {
      blackMassVolume: 25000,
      shareNMC: 75,
      metalPrices: 1.0,
      energyCostEU: 120,
      logisticsCost: 90,
      yieldRecovery: 90,
      pcamPremium: 3.5
    },
    optimiste: {
      blackMassVolume: 45000,
      shareNMC: 90,
      metalPrices: 1.2,
      energyCostEU: 80,
      logisticsCost: 60,
      yieldRecovery: 95,
      pcamPremium: 5
    }
  };

  // 2. État courant des inputs
  const [params, setParams] = useState(scenarios.conservateur);

  // 3. Constantes du marché (Base prices en $/kg ou €/kg approx)
  const BASE_PRICES = {
    Lithium: 20, // Li2CO3 eq
    Nickel: 18,  // Sulfate
    Cobalt: 35,  // Sulfate
    Manganese: 2,
    pCAM_Asia_Import: 18 // Prix benchmark importé
  };

  // Composition Black Mass (Hypothétique simplifiée pour modèle)
  // NMC 811 approx: Ni 25%, Co 3%, Mn 3%, Li 4% dans la black mass
  const BLACK_MASS_COMPOSITION = {
    NMC: { Ni: 0.25, Co: 0.05, Mn: 0.05, Li: 0.04 },
    LFP: { Ni: 0.00, Co: 0.00, Mn: 0.00, Li: 0.035 } // LFP a moins de valeur
  };

  const loadScenario = (type) => {
    setParams(scenarios[type]);
  };

  // --- MOTEUR DE CALCUL ---
  
  const calculateEconomics = () => {
    // 1. Volumes de métaux entrants (Tonnes)
    const totalBM = params.blackMassVolume;
    const volNMC = totalBM * (params.shareNMC / 100);
    const volLFP = totalBM * (1 - params.shareNMC / 100);

    // Récupération avec rendement
    const efficiency = params.yieldRecovery / 100;

    const metals = {
      Ni: (volNMC * BLACK_MASS_COMPOSITION.NMC.Ni * efficiency),
      Co: (volNMC * BLACK_MASS_COMPOSITION.NMC.Co * efficiency),
      Li: ((volNMC * BLACK_MASS_COMPOSITION.NMC.Li + volLFP * BLACK_MASS_COMPOSITION.LFP.Li) * efficiency),
      Mn: (volNMC * BLACK_MASS_COMPOSITION.NMC.Mn * efficiency)
    };

    // 2. Valeur "Cycle Ouvert" (Vente des sels métalliques)
    // Prix ajustés par le facteur scénario
    const pNi = BASE_PRICES.Nickel * params.metalPrices;
    const pCo = BASE_PRICES.Cobalt * params.metalPrices;
    const pLi = BASE_PRICES.Lithium * params.metalPrices;
    const pMn = BASE_PRICES.Manganese;

    const revenueOpenCycle = (metals.Ni * pNi + metals.Co * pCo + metals.Li * pLi + metals.Mn * pMn) * 1000; // en €
    
    // Coûts Opérationnels Cycle Ouvert (Hydrométallurgie seule)
    // Hypothèse: Coût processing ~ 2500€/t de Black Mass
    const costHydro = totalBM * 2500; 
    const marginOpenCycle = revenueOpenCycle - costHydro;

    // 3. Valeur "Cycle Fermé" (Production pCAM en Europe)
    // On suppose qu'on transforme Ni, Co, Mn en pCAM. Le Li est vendu à part (car pCAM = précurseur cathode sans Li)
    // Ratio: 1kg de pCAM nécessite ~0.6kg de métaux (Ni+Co+Mn). 
    // Simplification: On produit du pCAM avec le Ni/Co/Mn dispo et on complète ou on vend l'excès.
    // Supposons qu'on valorise tout le Ni/Co/Mn sous forme de pCAM.
    
    const massMetalsPCAM = metals.Ni + metals.Co + metals.Mn;
    const pcamVolume = massMetalsPCAM / 0.6; // Estimation grossière masse pCAM produite
    
    // Prix de vente pCAM Local = Prix Asie + Premium (Logistique évitée + CO2 + Sécurité)
    const pricePCAM_EU = BASE_PRICES.pCAM_Asia_Import + params.pcamPremium;
    
    const revenuePCAM = pcamVolume * pricePCAM_EU * 1000;
    const revenueLi_Closed = metals.Li * pLi * 1000; // Le Lithium est toujours vendu ou envoyé en cathodier
    
    const totalRevenueClosed = revenuePCAM + revenueLi_Closed;

    // Coûts Opérationnels Cycle Fermé (Hydro + pCAM process)
    // Surcoût énergétique Europe vs Asie
    const energyPenalty = (params.energyCostEU - 80) * 1000; // Impact approximatif
    const costPCAMProcessing = pcamVolume * 1500; // Coût transformation sels -> pCAM
    const totalCostClosed = costHydro + costPCAMProcessing + (totalBM * (params.logisticsCost / 10)); // Logistique interne

    const marginClosedCycle = totalRevenueClosed - totalCostClosed;

    return {
      metals,
      financials: {
        open: { revenue: revenueOpenCycle, cost: costHydro, margin: marginOpenCycle },
        closed: { revenue: totalRevenueClosed, cost: totalCostClosed, margin: marginClosedCycle }
      },
      volumes: {
        pcam: pcamVolume
      }
    };
  };

  const results = calculateEconomics();
  
  // Données pour les graphiques
  const chartDataComparison = [
    {
      name: 'Cycle Ouvert (Sels)',
      Revenu: (results.financials.open.revenue / 1000000).toFixed(1),
      Coût: (results.financials.open.cost / 1000000).toFixed(1),
      Marge: (results.financials.open.margin / 1000000).toFixed(1),
    },
    {
      name: 'Cycle Fermé (pCAM EU)',
      Revenu: (results.financials.closed.revenue / 1000000).toFixed(1),
      Coût: (results.financials.closed.cost / 1000000).toFixed(1),
      Marge: (results.financials.closed.margin / 1000000).toFixed(1),
    },
  ];

  return (
    <div className="bg-slate-50 min-h-screen text-slate-800 font-sans">
      
      {/* HEADER */}
      <header className="bg-slate-900 text-white p-4 shadow-lg sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Factory className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Relocalisation pCAM Europe</h1>
              <p className="text-xs text-slate-400">Simulateur Stratégique & Technico-Économique • Projet ESM 2025</p>
            </div>
          </div>
          
          <div className="flex bg-slate-800 rounded-lg p-1">
            <button 
              onClick={() => setActiveTab('dashboard')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'dashboard' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:text-white'}`}
            >
              Tableau de Bord
            </button>
            <button 
              onClick={() => setActiveTab('inputs')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'inputs' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:text-white'}`}
            >
              Paramètres & Scénarios
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6">
        
        {/* --- ONGLET DASHBOARD --- */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6 animate-fadeIn">
            
            {/* KPI ROW */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <KpiCard 
                title="Volume Black Mass" 
                value={`${params.blackMassVolume.toLocaleString()} t`} 
                subtext={`Dont ${params.shareNMC}% NMC`}
                color="blue"
              />
              <KpiCard 
                title="Production pCAM Est." 
                value={`${Math.round(results.volumes.pcam).toLocaleString()} t`} 
                subtext="Basé sur contenu métal récupéré"
                color="green"
              />
              <KpiCard 
                title="Marge Cycle Ouvert" 
                value={`${(results.financials.open.margin / 1000000).toFixed(1)} M€`} 
                subtext="Vente sels & métaux"
                color="amber"
              />
              <KpiCard 
                title="Marge Cycle Fermé" 
                value={`${(results.financials.closed.margin / 1000000).toFixed(1)} M€`} 
                subtext="Production locale pCAM"
                color={results.financials.closed.margin > results.financials.open.margin ? "green" : "red"}
              />
            </div>

            {/* CHARTS ROW */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Main Chart */}
              <Card className="lg:col-span-2 p-6">
                <SectionHeader icon={TrendingUp} title="Comparaison Économique : Cycle Ouvert vs Fermé" />
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartDataComparison} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} />
                      <YAxis unit=" M€" axisLine={false} tickLine={false} />
                      <Tooltip 
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        cursor={{ fill: '#f8fafc' }}
                      />
                      <Legend />
                      <Bar dataKey="Revenu" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Coût" fill="#ef4444" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Marge" fill="#10b981" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-4 p-4 bg-slate-50 rounded-lg text-sm text-slate-600 border border-slate-100">
                  <strong>Analyse :</strong> {results.financials.closed.margin > results.financials.open.margin 
                    ? "Le scénario 'Cycle Fermé' (relocalisation pCAM) est économiquement supérieur. La valeur ajoutée de la transformation compense les coûts énergétiques et opérationnels européens."
                    : "Le scénario 'Cycle Ouvert' est actuellement plus rentable. Les coûts de transformation pCAM en Europe (énergie, main d'œuvre) pèsent trop lourd face à la vente directe des sels recyclés."}
                </div>
              </Card>

              {/* Sensitivity / Context */}
              <div className="space-y-6">
                <Card className="p-6">
                  <SectionHeader icon={Info} title="Contexte Stratégique" />
                  <div className="space-y-4 text-sm">
                    <div className="flex justify-between items-center pb-2 border-b border-slate-100">
                      <span className="text-slate-600">Objectif Souveraineté</span>
                      <span className="font-bold text-blue-600">Critique</span>
                    </div>
                    <div className="flex justify-between items-center pb-2 border-b border-slate-100">
                      <span className="text-slate-600">Passeport Batterie</span>
                      <span className="font-bold text-green-600">Actif (2027)</span>
                    </div>
                    <div className="flex justify-between items-center pb-2 border-b border-slate-100">
                      <span className="text-slate-600">Réglementation Recyclage</span>
                      <span className="font-bold text-slate-800">90% Co/Ni (2031)</span>
                    </div>
                    
                    <div className="mt-4 p-3 bg-blue-50 text-blue-800 rounded-lg text-xs">
                      "Est-il plus rentable de vendre les métaux rares (Cycle Ouvert) ou de fabriquer des pCAM (Cycle Fermé) ?"
                    </div>
                  </div>
                </Card>

                <Card className="p-6">
                  <h4 className="font-bold text-slate-700 mb-4">Actions Rapides (Scénarios)</h4>
                  <div className="grid grid-cols-1 gap-2">
                    <button onClick={() => loadScenario('optimiste')} className="flex items-center justify-between p-3 border border-green-200 bg-green-50 rounded-lg hover:bg-green-100 transition text-green-800">
                      <span className="font-medium">Optimiste</span>
                      <TrendingUp className="w-4 h-4" />
                    </button>
                    <button onClick={() => loadScenario('conservateur')} className="flex items-center justify-between p-3 border border-blue-200 bg-blue-50 rounded-lg hover:bg-blue-100 transition text-blue-800">
                      <span className="font-medium">Conservateur (Base)</span>
                      <Save className="w-4 h-4" />
                    </button>
                    <button onClick={() => loadScenario('pessimiste')} className="flex items-center justify-between p-3 border border-red-200 bg-red-50 rounded-lg hover:bg-red-100 transition text-red-800">
                      <span className="font-medium">Pessimiste</span>
                      <AlertTriangle className="w-4 h-4" />
                    </button>
                  </div>
                </Card>
              </div>
            </div>
          </div>
        )}

        {/* --- ONGLET PARAMETRES --- */}
        {activeTab === 'inputs' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fadeIn">
            
            {/* AXE 1: OFFRE & VOLUME */}
            <Card className="p-6">
              <SectionHeader icon={RotateCcw} title="1. Estimation Offre (Black Mass)" />
              <InputGroup 
                label="Volume Black Mass Europe (2030)" 
                unit="Tonnes" 
                min={5000} max={100000} step={1000}
                value={params.blackMassVolume} 
                onChange={(v) => setParams({...params, blackMassVolume: v})}
                help="Basé sur prévisions EOL VE et scraps industriels"
              />
              <InputGroup 
                label="Part Chimie NMC (%)" 
                unit="%" 
                min={0} max={100} 
                value={params.shareNMC} 
                onChange={(v) => setParams({...params, shareNMC: v})}
                help="Le reste est supposé être LFP (moins de valeur)"
              />
               <InputGroup 
                label="Rendement Récupération Co/Ni" 
                unit="%" 
                min={50} max={99} 
                value={params.yieldRecovery} 
                onChange={(v) => setParams({...params, yieldRecovery: v})}
                help="Objectif UE 2031 : >90%"
              />
            </Card>

            {/* AXE 3: COMPÉTITIVITÉ & COÛTS */}
            <Card className="p-6">
              <SectionHeader icon={Euro} title="3. Coûts & Marché" />
              <InputGroup 
                label="Prix Marché Métaux (Index)" 
                unit="x Base" 
                min={0.5} max={2.0} step={0.1}
                value={params.metalPrices} 
                onChange={(v) => setParams({...params, metalPrices: v})}
                help="1.0 = Prix actuels moyens. Influence le revenu des deux cycles."
              />
              <InputGroup 
                label="Coût Électricité Europe" 
                unit="€/MWh" 
                min={40} max={300} 
                value={params.energyCostEU} 
                onChange={(v) => setParams({...params, energyCostEU: v})}
                help="Facteur critique pour l'hydrométallurgie"
              />
              <InputGroup 
                label="Coût Logistique Interne" 
                unit="€/Tonne" 
                min={20} max={200} 
                value={params.logisticsCost} 
                onChange={(v) => setParams({...params, logisticsCost: v})}
                help="Transport Black Mass vers usine Hydro/pCAM"
              />
               <InputGroup 
                label="Premium 'Made in EU'" 
                unit="€/kg pCAM" 
                min={0} max={10} step={0.5}
                value={params.pcamPremium} 
                onChange={(v) => setParams({...params, pcamPremium: v})}
                help="Valeur ajoutée verte/souveraine vs import Asie"
              />
            </Card>

            {/* Note Explicative */}
            <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-bold text-slate-800 mb-2 flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Détail de la Modélisation
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-600">
                <div>
                  <h4 className="font-semibold text-slate-900 mb-1">Cycle Ouvert (Export/Vente Sels)</h4>
                  <ul className="list-disc pl-4 space-y-1">
                    <li>Revenus = Vente sels sulfates (Ni, Co, Mn) + Li2CO3 au cours du marché.</li>
                    <li>Coûts = Achat Black Mass + OPEX Hydrométallurgie simple.</li>
                    <li>Risque = Dépendance aux prix volatils des métaux bruts.</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 mb-1">Cycle Fermé (Production pCAM)</h4>
                  <ul className="list-disc pl-4 space-y-1">
                    <li>Revenus = Vente pCAM (Ni+Co+Mn) + Vente Lithium séparé.</li>
                    <li>Coûts = Coûts Cycle Ouvert + OPEX pCAM (Précipitation, Énergie intensive) + Logistique fine.</li>
                    <li>Avantage = Capture de la marge de transformation + Sécurité d'approvisionnement pour Gigafactories.</li>
                  </ul>
                </div>
              </div>
            </div>

          </div>
        )}
      </main>
    </div>
  );
}
