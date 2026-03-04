import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

interface RouteContext {
  params: Promise<{ marketId: string }>;
}

export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  try {
    const { marketId } = await context.params;

    if (!marketId) {
      return NextResponse.json(
        { error: "Market ID is required" },
        { status: 400 }
      );
    }

    // Fetch recommendations for this market from the performance view
    const { data: recommendations, error: recError } = await supabase
      .from("v_closed_markets_performance")
      .select("*")
      .eq("market_id", marketId)
      .order("recommendation_created_at", { ascending: true });

    if (recError) {
      console.error("Error fetching market recommendations:", recError);
      return NextResponse.json(
        { error: "Failed to fetch market performance data" },
        { status: 500 }
      );
    }

    if (!recommendations || recommendations.length === 0) {
      return NextResponse.json(
        { error: "No performance data found for this market" },
        { status: 404 }
      );
    }

    // Extract market info from first recommendation
    const marketInfo = {
      id: recommendations[0].market_id,
      conditionId: recommendations[0].condition_id,
      question: recommendations[0].question,
      description: "", // Not in view, would need separate query if needed
      eventType: recommendations[0].event_type,
      resolvedOutcome: recommendations[0].resolved_outcome,
      resolutionDate: recommendations[0].resolution_date,
      slug: recommendations[0].question && recommendations[0].market_id
        ? generateMarketSlug(recommendations[0].question, recommendations[0].market_id)
        : `market-${recommendations[0].market_id || marketId}`,
    };

    // Fetch agent signals for this market (if available)
    const { data: agentSignals, error: signalsError } = await supabase
      .from("agent_signals")
      .select("agent_name, direction, agent_probability, agent_confidence")
      .eq("market_id", marketId)
      .order("created_at", { ascending: false })
      .limit(50);

    if (signalsError) {
      console.error("Error fetching agent signals:", signalsError);
    }

    // Transform recommendations to include outcome data
    const recommendationsWithOutcome = recommendations.map(rec => ({
      id: rec.recommendation_id,
      marketId: rec.market_id,
      direction: rec.direction,
      confidence: rec.confidence,
      fairProbability: rec.fair_probability,
      marketEdge: rec.market_edge,
      expectedValue: rec.expected_value,
      entryZoneMin: rec.entry_zone_min,
      entryZoneMax: rec.entry_zone_max,
      explanation: rec.explanation,
      createdAt: rec.recommendation_created_at,
      actualOutcome: rec.resolved_outcome,
      wasCorrect: rec.recommendation_was_correct,
      roiRealized: rec.roi_realized,
      edgeCaptured: rec.edge_captured,
      marketPriceAtRecommendation: rec.market_probability_at_recommendation,
      resolutionDate: rec.resolution_date,
      entryPrice: rec.market_probability_at_recommendation,
      // Exit price would be final resolution price or intermediate price if available
      exitPrice: rec.resolved_outcome === "YES" ? 1.0 : 0.0,
    }));

    // Calculate performance metrics
    const metrics = calculateMarketMetrics(recommendationsWithOutcome);

    return NextResponse.json({
      market: marketInfo,
      recommendations: recommendationsWithOutcome,
      metrics,
      agentSignals: agentSignals || [],
    });
  } catch (error) {
    console.error("Error in market performance detail API:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

function generateMarketSlug(question: string, marketId: string): string {
  const slug = question
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .substring(0, 60);
  
  const idSuffix = marketId.substring(0, 8);
  return `${slug}-${idSuffix}`;
}

function calculateMarketMetrics(recommendations: any[]) {
  if (recommendations.length === 0) {
    return {
      accuracy: {
        total: 0,
        correct: 0,
        percentage: 0,
        byConfidence: {
          high: { total: 0, correct: 0, percentage: 0 },
          moderate: { total: 0, correct: 0, percentage: 0 },
          low: { total: 0, correct: 0, percentage: 0 },
        },
      },
      roi: {
        total: 0,
        average: 0,
        best: 0,
        worst: 0,
        byRecommendation: [],
      },
    };
  }

  // Calculate accuracy
  const correctCount = recommendations.filter(r => r.wasCorrect).length;
  const accuracyPercentage = (correctCount / recommendations.length) * 100;

  // Calculate accuracy by confidence
  const byConfidence = {
    high: { total: 0, correct: 0, percentage: 0 },
    moderate: { total: 0, correct: 0, percentage: 0 },
    low: { total: 0, correct: 0, percentage: 0 },
  };

  recommendations.forEach(rec => {
    const conf = rec.confidence as "high" | "moderate" | "low";
    byConfidence[conf].total++;
    if (rec.wasCorrect) {
      byConfidence[conf].correct++;
    }
  });

  Object.keys(byConfidence).forEach(key => {
    const conf = key as "high" | "moderate" | "low";
    if (byConfidence[conf].total > 0) {
      byConfidence[conf].percentage = 
        (byConfidence[conf].correct / byConfidence[conf].total) * 100;
    }
  });

  // Calculate ROI metrics
  const roiValues = recommendations.map(r => r.roiRealized || 0);
  const totalROI = roiValues.reduce((sum, roi) => sum + roi, 0);
  const avgROI = totalROI / recommendations.length;
  const bestROI = Math.max(...roiValues);
  const worstROI = Math.min(...roiValues);

  const roiByRecommendation = recommendations.map(rec => ({
    id: rec.id,
    roi: rec.roiRealized || 0,
  }));

  return {
    accuracy: {
      total: recommendations.length,
      correct: correctCount,
      percentage: Math.round(accuracyPercentage * 100) / 100,
      byConfidence,
    },
    roi: {
      total: Math.round(totalROI * 100) / 100,
      average: Math.round(avgROI * 100) / 100,
      best: Math.round(bestROI * 100) / 100,
      worst: Math.round(worstROI * 100) / 100,
      byRecommendation: roiByRecommendation,
    },
  };
}
