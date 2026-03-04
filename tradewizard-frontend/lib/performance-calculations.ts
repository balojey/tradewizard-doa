/**
 * Performance Calculation Utilities
 * 
 * This module provides calculation functions for the Closed Markets Performance Viewer.
 * All calculations follow the specifications in the design document and handle edge cases
 * gracefully by returning null for invalid inputs.
 * 
 * @module performance-calculations
 */

/**
 * Polymarket trading fee (2% on winning positions only)
 */
const POLYMARKET_FEE = 0.02;

/**
 * Represents a single simulated trade based on an AI recommendation
 */
export interface SimulatedTrade {
  recommendationId: string;
  entryPrice: number;
  exitPrice: number;
  shares: number;
  entryFee: number;
  exitFee: number;
  grossProfitLoss: number;
  netProfitLoss: number;
  roi: number;
  timestamp: string;
}

/**
 * Represents cumulative performance at a point in time
 */
export interface CumulativePerformance {
  timestamp: string;
  cumulativePL: number;
  cumulativeROI: number;
  tradeCount: number;
}

/**
 * Summary of simulated portfolio performance
 */
export interface PortfolioSummary {
  totalPL: number;
  totalROI: number;
  winRate: number;
  avgWin: number;
  avgLoss: number;
}

/**
 * Complete simulated portfolio result
 */
export interface SimulatedPortfolio {
  trades: SimulatedTrade[];
  cumulative: CumulativePerformance[];
  summary: PortfolioSummary;
}

/**
 * Recommendation with outcome data for calculations
 */
export interface RecommendationWithOutcome {
  id: string;
  direction: 'LONG_YES' | 'LONG_NO' | 'NO_TRADE';
  marketPriceAtRecommendation: number;
  exitPrice?: number;
  actualOutcome: string;
  wasCorrect: boolean;
  createdAt: string;
  fairProbability: number;
  confidence: 'high' | 'moderate' | 'low';
}

/**
 * Accuracy metrics for recommendations
 */
export interface AccuracyMetrics {
  totalRecommendations: number;
  correctRecommendations: number;
  accuracyPercentage: number;
  averageConfidence: number;
  confidenceAccuracyCorrelation: number;
  byConfidence: {
    high: { total: number; correct: number; percentage: number };
    moderate: { total: number; correct: number; percentage: number };
    low: { total: number; correct: number; percentage: number };
  };
}

/**
 * Risk-adjusted performance metrics
 */
export interface RiskMetrics {
  sharpeRatio: number | null;
  maxDrawdown: number;
  volatility: number;
  riskAdjustedReturn: number | null;
}

/**
 * Calibration analysis metrics
 */
export interface CalibrationMetrics {
  calibrationError: number;
  avgConfidenceCorrect: number;
  avgConfidenceIncorrect: number;
  confidenceAccuracyCorrelation: number;
}

/**
 * Baseline strategy comparison results
 */
export interface BaselineComparison {
  buyAndHold: {
    roi: number;
    profitLoss: number;
  };
  randomStrategy: {
    roi: number;
    profitLoss: number;
    iterations: number;
  };
  aiPerformance: {
    roi: number;
    profitLoss: number;
  };
  statisticalSignificance: {
    pValue: number;
    isSignificant: boolean;
  };
}

/**
 * Task 3.1: Calculate simulated portfolio performance
 * 
 * Simulates profit/loss from following AI recommendations with a specified investment amount.
 * Applies Polymarket's 2% fee only on winning positions.
 * 
 * @param recommendations - Array of recommendations with outcome data
 * @param investmentAmount - Amount to invest per recommendation (in dollars)
 * @returns Simulated portfolio with trades, cumulative performance, and summary
 * 
 * @example
 * ```typescript
 * const portfolio = calculateSimulatedPortfolio(recommendations, 100);
 * console.log(`Total P/L: $${portfolio.summary.totalPL.toFixed(2)}`);
 * console.log(`Win Rate: ${portfolio.summary.winRate.toFixed(1)}%`);
 * ```
 */
export function calculateSimulatedPortfolio(
  recommendations: RecommendationWithOutcome[],
  investmentAmount: number
): SimulatedPortfolio {
  if (!recommendations || recommendations.length === 0 || investmentAmount <= 0) {
    return {
      trades: [],
      cumulative: [],
      summary: {
        totalPL: 0,
        totalROI: 0,
        winRate: 0,
        avgWin: 0,
        avgLoss: 0,
      },
    };
  }

  const trades: SimulatedTrade[] = [];
  const cumulative: CumulativePerformance[] = [];
  let cumulativePL = 0;

  // Filter out NO_TRADE recommendations
  const tradableRecs = recommendations.filter(rec => rec.direction !== 'NO_TRADE');

  tradableRecs.forEach((rec) => {
    const entryPrice = rec.marketPriceAtRecommendation;
    
    // Use exit price if available, otherwise use resolution price (1 for YES, 0 for NO)
    let exitPrice = rec.exitPrice;
    if (exitPrice === undefined || exitPrice === null) {
      exitPrice = rec.actualOutcome === 'YES' ? 1 : 0;
    }

    // Validate prices are in valid range [0, 1]
    if (entryPrice <= 0 || entryPrice > 1 || exitPrice < 0 || exitPrice > 1) {
      console.warn(`Invalid prices for recommendation ${rec.id}: entry=${entryPrice}, exit=${exitPrice}`);
      return; // Skip this recommendation
    }

    // Calculate shares purchased
    const shares = investmentAmount / entryPrice;

    // Calculate gross P/L
    const grossPL = shares * (exitPrice - entryPrice);

    // Apply fees only on winning positions (2% of gross profit)
    const fees = grossPL > 0 ? grossPL * POLYMARKET_FEE : 0;
    const netPL = grossPL - fees;

    // Calculate ROI as percentage
    const roi = (netPL / investmentAmount) * 100;

    trades.push({
      recommendationId: rec.id,
      entryPrice,
      exitPrice,
      shares,
      entryFee: 0, // Polymarket doesn't charge entry fees
      exitFee: fees,
      grossProfitLoss: grossPL,
      netProfitLoss: netPL,
      roi,
      timestamp: rec.createdAt,
    });

    cumulativePL += netPL;

    cumulative.push({
      timestamp: rec.createdAt,
      cumulativePL,
      cumulativeROI: (cumulativePL / (investmentAmount * trades.length)) * 100,
      tradeCount: trades.length,
    });
  });

  // Calculate summary statistics
  const wins = trades.filter(t => t.netProfitLoss > 0);
  const losses = trades.filter(t => t.netProfitLoss < 0);

  const summary: PortfolioSummary = {
    totalPL: cumulativePL,
    totalROI: trades.length > 0 ? (cumulativePL / (investmentAmount * trades.length)) * 100 : 0,
    winRate: trades.length > 0 ? (wins.length / trades.length) * 100 : 0,
    avgWin: wins.length > 0 ? wins.reduce((sum, t) => sum + t.netProfitLoss, 0) / wins.length : 0,
    avgLoss: losses.length > 0 ? losses.reduce((sum, t) => sum + t.netProfitLoss, 0) / losses.length : 0,
  };

  return {
    trades,
    cumulative,
    summary,
  };
}

/**
 * Task 3.3: Calculate accuracy metrics for recommendations
 * 
 * Calculates overall accuracy, accuracy by confidence level, and correlation
 * between confidence and accuracy.
 * 
 * @param recommendations - Array of recommendations with outcome data
 * @returns Accuracy metrics including overall and by-confidence breakdowns
 * 
 * @example
 * ```typescript
 * const metrics = calculateAccuracyMetrics(recommendations);
 * console.log(`Accuracy: ${metrics.accuracyPercentage.toFixed(1)}%`);
 * console.log(`High confidence accuracy: ${metrics.byConfidence.high.percentage.toFixed(1)}%`);
 * ```
 */
export function calculateAccuracyMetrics(
  recommendations: RecommendationWithOutcome[]
): AccuracyMetrics {
  if (!recommendations || recommendations.length === 0) {
    return {
      totalRecommendations: 0,
      correctRecommendations: 0,
      accuracyPercentage: 0,
      averageConfidence: 0,
      confidenceAccuracyCorrelation: 0,
      byConfidence: {
        high: { total: 0, correct: 0, percentage: 0 },
        moderate: { total: 0, correct: 0, percentage: 0 },
        low: { total: 0, correct: 0, percentage: 0 },
      },
    };
  }

  const total = recommendations.length;
  const correct = recommendations.filter(r => r.wasCorrect).length;
  const accuracyPercentage = (correct / total) * 100;

  // Calculate average confidence (convert confidence levels to numeric values)
  const confidenceValues = recommendations.map(r => {
    switch (r.confidence) {
      case 'high': return 3;
      case 'moderate': return 2;
      case 'low': return 1;
      default: return 2;
    }
  });
  const avgConfidence = confidenceValues.reduce((sum, val) => sum + val, 0) / total;

  // Calculate accuracy by confidence level
  const byConfidence = {
    high: calculateConfidenceAccuracy(recommendations, 'high'),
    moderate: calculateConfidenceAccuracy(recommendations, 'moderate'),
    low: calculateConfidenceAccuracy(recommendations, 'low'),
  };

  // Calculate correlation between confidence and accuracy
  const correlation = calculateCorrelation(
    confidenceValues,
    recommendations.map(r => r.wasCorrect ? 1 : 0)
  );

  return {
    totalRecommendations: total,
    correctRecommendations: correct,
    accuracyPercentage,
    averageConfidence: avgConfidence,
    confidenceAccuracyCorrelation: correlation,
    byConfidence,
  };
}

/**
 * Helper function to calculate accuracy for a specific confidence level
 */
function calculateConfidenceAccuracy(
  recommendations: RecommendationWithOutcome[],
  confidence: 'high' | 'moderate' | 'low'
): { total: number; correct: number; percentage: number } {
  const filtered = recommendations.filter(r => r.confidence === confidence);
  const total = filtered.length;
  const correct = filtered.filter(r => r.wasCorrect).length;
  const percentage = total > 0 ? (correct / total) * 100 : 0;

  return { total, correct, percentage };
}

/**
 * Task 3.5: Calculate risk-adjusted performance metrics
 * 
 * Calculates Sharpe ratio, maximum drawdown, and volatility for a series of returns.
 * Assumes risk-free rate of 0 for Sharpe ratio calculation.
 * 
 * @param returns - Array of return percentages (e.g., [5.2, -3.1, 8.7])
 * @returns Risk metrics including Sharpe ratio, max drawdown, and volatility
 * 
 * @example
 * ```typescript
 * const returns = trades.map(t => t.roi);
 * const risk = calculateRiskMetrics(returns);
 * console.log(`Sharpe Ratio: ${risk.sharpeRatio?.toFixed(2) ?? 'N/A'}`);
 * console.log(`Max Drawdown: ${risk.maxDrawdown.toFixed(2)}%`);
 * ```
 */
export function calculateRiskMetrics(returns: number[]): RiskMetrics {
  if (!returns || returns.length === 0) {
    return {
      sharpeRatio: null,
      maxDrawdown: 0,
      volatility: 0,
      riskAdjustedReturn: null,
    };
  }

  // Calculate average return
  const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;

  // Calculate volatility (standard deviation)
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
  const volatility = Math.sqrt(variance);

  // Calculate Sharpe ratio (assuming risk-free rate of 0)
  const sharpeRatio = volatility > 0 ? avgReturn / volatility : null;

  // Calculate maximum drawdown
  const maxDrawdown = calculateMaxDrawdown(returns);

  // Calculate risk-adjusted return (return per unit of volatility)
  const riskAdjustedReturn = volatility > 0 ? avgReturn / volatility : null;

  return {
    sharpeRatio,
    maxDrawdown,
    volatility,
    riskAdjustedReturn,
  };
}

/**
 * Helper function to calculate maximum drawdown from returns
 */
function calculateMaxDrawdown(returns: number[]): number {
  if (returns.length === 0) return 0;

  let peak = 0;
  let maxDrawdown = 0;
  let cumulative = 0;

  for (const ret of returns) {
    cumulative += ret;
    
    if (cumulative > peak) {
      peak = cumulative;
    }
    
    const drawdown = peak - cumulative;
    if (drawdown > maxDrawdown) {
      maxDrawdown = drawdown;
    }
  }

  return maxDrawdown;
}

/**
 * Task 3.7: Calculate calibration analysis metrics
 * 
 * Analyzes how well confidence levels correlate with actual outcomes.
 * Calculates calibration error and average confidence for correct vs incorrect predictions.
 * 
 * @param recommendations - Array of recommendations with outcome data
 * @returns Calibration metrics including error and confidence segmentation
 * 
 * @example
 * ```typescript
 * const calibration = calculateCalibrationMetrics(recommendations);
 * console.log(`Calibration Error: ${calibration.calibrationError.toFixed(3)}`);
 * console.log(`Avg Confidence (Correct): ${calibration.avgConfidenceCorrect.toFixed(2)}`);
 * ```
 */
export function calculateCalibrationMetrics(
  recommendations: RecommendationWithOutcome[]
): CalibrationMetrics {
  if (!recommendations || recommendations.length === 0) {
    return {
      calibrationError: 0,
      avgConfidenceCorrect: 0,
      avgConfidenceIncorrect: 0,
      confidenceAccuracyCorrelation: 0,
    };
  }

  // Calculate calibration error (mean absolute difference between predicted probability and outcome)
  const calibrationErrors = recommendations.map(rec => {
    const predicted = rec.fairProbability;
    const actual = rec.wasCorrect ? 1 : 0;
    return Math.abs(predicted - actual);
  });
  const calibrationError = calibrationErrors.reduce((sum, err) => sum + err, 0) / calibrationErrors.length;

  // Segment by correctness
  const correct = recommendations.filter(r => r.wasCorrect);
  const incorrect = recommendations.filter(r => !r.wasCorrect);

  // Calculate average confidence for each segment (using numeric values)
  const avgConfidenceCorrect = correct.length > 0
    ? correct.reduce((sum, r) => sum + confidenceToNumeric(r.confidence), 0) / correct.length
    : 0;

  const avgConfidenceIncorrect = incorrect.length > 0
    ? incorrect.reduce((sum, r) => sum + confidenceToNumeric(r.confidence), 0) / incorrect.length
    : 0;

  // Calculate correlation between confidence and accuracy
  const confidenceValues = recommendations.map(r => confidenceToNumeric(r.confidence));
  const accuracyValues = recommendations.map(r => r.wasCorrect ? 1 : 0);
  const correlation = calculateCorrelation(confidenceValues, accuracyValues);

  return {
    calibrationError,
    avgConfidenceCorrect,
    avgConfidenceIncorrect,
    confidenceAccuracyCorrelation: correlation,
  };
}

/**
 * Helper function to convert confidence level to numeric value
 */
function confidenceToNumeric(confidence: 'high' | 'moderate' | 'low'): number {
  switch (confidence) {
    case 'high': return 3;
    case 'moderate': return 2;
    case 'low': return 1;
    default: return 2;
  }
}

/**
 * Task 3.8: Calculate baseline strategy comparison
 * 
 * Compares AI performance against buy-and-hold and random strategy baselines.
 * Uses Monte Carlo simulation for random strategy (1000 iterations).
 * 
 * @param recommendations - Array of recommendations with outcome data
 * @param investmentAmount - Amount invested per recommendation
 * @param firstRecommendationPrice - Market price at first recommendation
 * @param finalPrice - Final market resolution price (1 for YES, 0 for NO)
 * @returns Baseline comparison with statistical significance
 * 
 * @example
 * ```typescript
 * const comparison = calculateBaselineComparison(recommendations, 100, 0.45, 1);
 * console.log(`AI ROI: ${comparison.aiPerformance.roi.toFixed(2)}%`);
 * console.log(`Buy & Hold ROI: ${comparison.buyAndHold.roi.toFixed(2)}%`);
 * console.log(`Significant: ${comparison.statisticalSignificance.isSignificant}`);
 * ```
 */
export function calculateBaselineComparison(
  recommendations: RecommendationWithOutcome[],
  investmentAmount: number,
  firstRecommendationPrice: number,
  finalPrice: number
): BaselineComparison {
  // Calculate AI performance
  const aiPortfolio = calculateSimulatedPortfolio(recommendations, investmentAmount);
  const aiPerformance = {
    roi: aiPortfolio.summary.totalROI,
    profitLoss: aiPortfolio.summary.totalPL,
  };

  // Calculate buy-and-hold baseline
  const buyAndHoldShares = investmentAmount / firstRecommendationPrice;
  const buyAndHoldGrossPL = buyAndHoldShares * (finalPrice - firstRecommendationPrice);
  const buyAndHoldFees = buyAndHoldGrossPL > 0 ? buyAndHoldGrossPL * POLYMARKET_FEE : 0;
  const buyAndHoldNetPL = buyAndHoldGrossPL - buyAndHoldFees;
  const buyAndHoldROI = (buyAndHoldNetPL / investmentAmount) * 100;

  const buyAndHold = {
    roi: buyAndHoldROI,
    profitLoss: buyAndHoldNetPL,
  };

  // Calculate random strategy baseline (Monte Carlo simulation)
  const randomIterations = 1000;
  const randomResults: number[] = [];

  for (let i = 0; i < randomIterations; i++) {
    // Simulate random entry/exit points
    const randomEntry = Math.random();
    const randomExit = Math.random();
    
    const shares = investmentAmount / randomEntry;
    const grossPL = shares * (randomExit - randomEntry);
    const fees = grossPL > 0 ? grossPL * POLYMARKET_FEE : 0;
    const netPL = grossPL - fees;
    const roi = (netPL / investmentAmount) * 100;
    
    randomResults.push(roi);
  }

  const randomAvgROI = randomResults.reduce((sum, roi) => sum + roi, 0) / randomIterations;
  const randomStrategy = {
    roi: randomAvgROI,
    profitLoss: (randomAvgROI / 100) * investmentAmount,
    iterations: randomIterations,
  };

  // Calculate statistical significance (t-test)
  const aiReturns = aiPortfolio.trades.map(t => t.roi);
  const significance = calculateTTest(aiReturns, randomResults);

  return {
    buyAndHold,
    randomStrategy,
    aiPerformance,
    statisticalSignificance: significance,
  };
}

/**
 * Helper function to calculate Pearson correlation coefficient
 */
function calculateCorrelation(x: number[], y: number[]): number {
  if (x.length !== y.length || x.length === 0) return 0;

  const n = x.length;
  const sumX = x.reduce((sum, val) => sum + val, 0);
  const sumY = y.reduce((sum, val) => sum + val, 0);
  const sumXY = x.reduce((sum, val, i) => sum + val * y[i], 0);
  const sumX2 = x.reduce((sum, val) => sum + val * val, 0);
  const sumY2 = y.reduce((sum, val) => sum + val * val, 0);

  const numerator = n * sumXY - sumX * sumY;
  const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));

  if (denominator === 0) return 0;

  return numerator / denominator;
}

/**
 * Helper function to perform two-sample t-test
 */
function calculateTTest(
  sample1: number[],
  sample2: number[]
): { pValue: number; isSignificant: boolean } {
  if (sample1.length === 0 || sample2.length === 0) {
    return { pValue: 1, isSignificant: false };
  }

  const mean1 = sample1.reduce((sum, val) => sum + val, 0) / sample1.length;
  const mean2 = sample2.reduce((sum, val) => sum + val, 0) / sample2.length;

  const variance1 = sample1.reduce((sum, val) => sum + Math.pow(val - mean1, 2), 0) / (sample1.length - 1);
  const variance2 = sample2.reduce((sum, val) => sum + Math.pow(val - mean2, 2), 0) / (sample2.length - 1);

  const pooledVariance = ((sample1.length - 1) * variance1 + (sample2.length - 1) * variance2) / 
                         (sample1.length + sample2.length - 2);

  const standardError = Math.sqrt(pooledVariance * (1 / sample1.length + 1 / sample2.length));

  if (standardError === 0) {
    return { pValue: 1, isSignificant: false };
  }

  const tStatistic = (mean1 - mean2) / standardError;

  // Simplified p-value approximation (for demonstration)
  // In production, use a proper statistical library
  const pValue = 2 * (1 - normalCDF(Math.abs(tStatistic)));

  return {
    pValue,
    isSignificant: pValue < 0.05,
  };
}

/**
 * Helper function for normal cumulative distribution function (approximation)
 */
function normalCDF(z: number): number {
  const t = 1 / (1 + 0.2316419 * Math.abs(z));
  const d = 0.3989423 * Math.exp(-z * z / 2);
  const prob = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  
  return z > 0 ? 1 - prob : prob;
}
