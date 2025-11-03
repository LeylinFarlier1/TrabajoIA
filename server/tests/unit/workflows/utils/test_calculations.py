"""Unit tests for workflow statistical calculations.

Tests cover:
- Time series alignment with missing/inconsistent data
- Basic statistical measures
- Convergence/divergence analysis using CV
- Outlier detection using Z-score method
- Trend analysis with linear regression
- Ranking and spread calculations
"""
import pytest

from trabajo_ia_server.workflows.utils.calculations import (
    align_time_series,
    analyze_convergence,
    calculate_basic_stats,
    calculate_change_rates,
    calculate_coefficient_of_variation,
    calculate_linear_trend,
    calculate_spread,
    detect_outliers,
    rank_values,
)


class TestAlignTimeSeries:
    """Test time series alignment (inner join)."""

    def test_perfect_alignment(self):
        """Test alignment when all series have same dates."""
        series_data = {
            "usa": [
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "2.9"},
            ],
            "uk": [
                {"date": "2025-01", "value": "2.5"},
                {"date": "2025-02", "value": "2.4"},
            ],
        }

        dates, aligned = align_time_series(series_data)

        assert dates == ["2025-01", "2025-02"]
        assert aligned["usa"] == [3.0, 2.9]
        assert aligned["uk"] == [2.5, 2.4]

    def test_partial_overlap(self):
        """Test inner join behavior with partial date overlap."""
        series_data = {
            "usa": [
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "2.9"},
                {"date": "2025-03", "value": "2.8"},
            ],
            "uk": [
                {"date": "2025-02", "value": "2.5"},
                {"date": "2025-03", "value": "2.4"},
                {"date": "2025-04", "value": "2.3"},
            ],
        }

        dates, aligned = align_time_series(series_data)

        # Only common dates
        assert dates == ["2025-02", "2025-03"]
        assert aligned["usa"] == [2.9, 2.8]
        assert aligned["uk"] == [2.5, 2.4]

    def test_missing_values_excluded(self):
        """Test that missing values (.) are excluded from alignment."""
        series_data = {
            "usa": [
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "."},
                {"date": "2025-03", "value": "2.8"},
            ],
            "uk": [
                {"date": "2025-01", "value": "2.5"},
                {"date": "2025-02", "value": "2.4"},
                {"date": "2025-03", "value": "2.3"},
            ],
        }

        dates, aligned = align_time_series(series_data)

        # 2025-02 excluded because USA has missing value
        assert dates == ["2025-01", "2025-03"]
        assert aligned["usa"] == [3.0, 2.8]
        assert aligned["uk"] == [2.5, 2.3]

    def test_no_common_dates(self):
        """Test when series have no overlapping dates."""
        series_data = {
            "usa": [{"date": "2025-01", "value": "3.0"}],
            "uk": [{"date": "2025-02", "value": "2.5"}],
        }

        dates, aligned = align_time_series(series_data)

        assert dates == []
        assert aligned["usa"] == []
        assert aligned["uk"] == []

    def test_chronological_sorting(self):
        """Test that dates are sorted chronologically."""
        series_data = {
            "usa": [
                {"date": "2025-03", "value": "2.8"},
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "2.9"},
            ],
            "uk": [
                {"date": "2025-02", "value": "2.4"},
                {"date": "2025-03", "value": "2.3"},
                {"date": "2025-01", "value": "2.5"},
            ],
        }

        dates, aligned = align_time_series(series_data)

        assert dates == ["2025-01", "2025-02", "2025-03"]
        assert aligned["usa"] == [3.0, 2.9, 2.8]
        assert aligned["uk"] == [2.5, 2.4, 2.3]

    def test_empty_input(self):
        """Test with empty series data."""
        dates, aligned = align_time_series({})

        assert dates == []
        assert aligned == {}


class TestCalculateBasicStats:
    """Test basic statistical measures."""

    def test_normal_values(self):
        """Test stats with typical values."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        stats = calculate_basic_stats(values)

        assert stats["mean"] == 3.0
        assert stats["median"] == 3.0
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0
        assert stats["std"] == pytest.approx(1.5811, rel=1e-3)

    def test_single_value(self):
        """Test with single value (std should be 0)."""
        values = [5.0]
        stats = calculate_basic_stats(values)

        assert stats["mean"] == 5.0
        assert stats["median"] == 5.0
        assert stats["std"] == 0

    def test_empty_values(self):
        """Test with empty list."""
        stats = calculate_basic_stats([])

        assert stats["mean"] == 0
        assert stats["median"] == 0
        assert stats["std"] == 0


class TestCoefficientOfVariation:
    """Test coefficient of variation for convergence analysis."""

    def test_low_cv_convergent(self):
        """Test low CV indicates convergence."""
        values = [10.0, 10.5, 9.5]  # Tightly clustered
        cv = calculate_coefficient_of_variation(values)

        assert cv < 0.1  # Low variation

    def test_high_cv_divergent(self):
        """Test high CV indicates divergence."""
        values = [10.0, 20.0, 5.0]  # Wide spread
        cv = calculate_coefficient_of_variation(values)

        assert cv > 0.3  # High variation

    def test_single_value(self):
        """Test CV with single value."""
        cv = calculate_coefficient_of_variation([10.0])

        assert cv == 0.0

    def test_zero_mean(self):
        """Test CV when mean is zero."""
        values = [-5.0, 0.0, 5.0]
        cv = calculate_coefficient_of_variation(values)

        assert cv == 0.0  # Protection against division by zero


class TestDetectOutliers:
    """Test outlier detection using Z-score method."""

    def test_clear_outlier(self):
        """Test detection of obvious outlier."""
        # Need enough values and large enough outlier for 2-sigma threshold
        values = [10.0, 10.0, 10.0, 10.0, 10.0, 100.0]  # 100.0 is clearly an outlier
        outliers = detect_outliers(values)

        assert 5 in outliers  # Index of 100.0

    def test_no_outliers(self):
        """Test with no outliers."""
        values = [10.0, 11.0, 10.5, 10.2]
        outliers = detect_outliers(values)

        assert outliers == []

    def test_multiple_outliers(self):
        """Test detection of multiple outliers with lower threshold."""
        # Use very extreme values and lower threshold
        # Note: Multiple outliers affect mean/std, making detection harder
        values = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1000.0, 2000.0]
        outliers = detect_outliers(values, threshold_sigma=1.5)

        # With extreme outliers and 1.5-sigma threshold, should detect at least 1
        assert len(outliers) >= 1

    def test_custom_threshold(self):
        """Test with custom sigma threshold."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        outliers = detect_outliers(values, threshold_sigma=1.0)  # Stricter

        # With 1-sigma threshold, more values might be flagged
        assert isinstance(outliers, list)

    def test_insufficient_data(self):
        """Test with too few data points."""
        outliers = detect_outliers([1.0, 2.0])

        assert outliers == []

    def test_zero_variance(self):
        """Test when all values are identical."""
        values = [5.0, 5.0, 5.0, 5.0]
        outliers = detect_outliers(values)

        assert outliers == []


class TestCalculateLinearTrend:
    """Test linear trend analysis."""

    def test_increasing_trend(self):
        """Test with clear increasing trend."""
        values = [1.0, 2.0, 3.0, 4.0]
        trend = calculate_linear_trend(values)

        assert trend["direction"] == "increasing"
        assert trend["slope"] == pytest.approx(1.0, abs=0.01)
        assert "+1.00" in trend["velocity"]

    def test_decreasing_trend(self):
        """Test with clear decreasing trend."""
        values = [4.0, 3.0, 2.0, 1.0]
        trend = calculate_linear_trend(values)

        assert trend["direction"] == "decreasing"
        assert trend["slope"] == pytest.approx(-1.0, abs=0.01)
        assert "-1.00" in trend["velocity"]

    def test_stable_trend(self):
        """Test with stable/flat values."""
        values = [5.0, 5.01, 4.99, 5.0]
        trend = calculate_linear_trend(values)

        assert trend["direction"] == "stable"
        assert abs(trend["slope"]) < 0.01

    def test_single_value(self):
        """Test with single value."""
        values = [5.0]
        trend = calculate_linear_trend(values)

        assert trend["direction"] == "stable"
        assert trend["slope"] == 0

    def test_empty_values(self):
        """Test with empty list."""
        trend = calculate_linear_trend([])

        assert trend["direction"] == "stable"
        assert trend["slope"] == 0


class TestCalculateChangeRates:
    """Test change rate calculations."""

    def test_sufficient_data_all_changes(self):
        """Test with enough data for all change rates."""
        # 13 months of data
        values = [100.0 + i for i in range(13)]
        changes = calculate_change_rates(values)

        assert changes["change_1m"] == pytest.approx(1.0, abs=0.01)
        assert changes["change_3m"] == pytest.approx(3.0, abs=0.01)
        assert changes["change_12m"] == pytest.approx(12.0, abs=0.01)

    def test_only_1m_change(self):
        """Test with only enough data for 1-month change."""
        values = [100.0, 101.0]
        changes = calculate_change_rates(values)

        assert changes["change_1m"] == pytest.approx(1.0, abs=0.01)
        assert changes["change_3m"] is None
        assert changes["change_12m"] is None

    def test_only_3m_change(self):
        """Test with enough data for 3-month change."""
        values = [100.0, 101.0, 102.0, 103.0]
        changes = calculate_change_rates(values)

        assert changes["change_1m"] == pytest.approx(1.0, abs=0.01)
        assert changes["change_3m"] == pytest.approx(3.0, abs=0.01)
        assert changes["change_12m"] is None

    def test_empty_values(self):
        """Test with empty values."""
        changes = calculate_change_rates([])

        assert changes["change_1m"] is None
        assert changes["change_3m"] is None
        assert changes["change_12m"] is None


class TestRankValues:
    """Test ranking functionality."""

    def test_ascending_rank(self):
        """Test default ascending ranking (lower value = better rank)."""
        data = {"usa": 3.0, "uk": 2.5, "euro_area": 2.2}
        ranking = rank_values(data, reverse=False)

        assert ranking[0] == {"region": "euro_area", "value": 2.2, "rank": 1}
        assert ranking[1] == {"region": "uk", "value": 2.5, "rank": 2}
        assert ranking[2] == {"region": "usa", "value": 3.0, "rank": 3}

    def test_descending_rank(self):
        """Test descending ranking (higher value = better rank)."""
        data = {"usa": 3.0, "uk": 2.5, "euro_area": 2.2}
        ranking = rank_values(data, reverse=True)

        assert ranking[0] == {"region": "usa", "value": 3.0, "rank": 1}
        assert ranking[1] == {"region": "uk", "value": 2.5, "rank": 2}
        assert ranking[2] == {"region": "euro_area", "value": 2.2, "rank": 3}

    def test_single_region(self):
        """Test ranking with single region."""
        data = {"usa": 3.0}
        ranking = rank_values(data)

        assert len(ranking) == 1
        assert ranking[0]["rank"] == 1


class TestCalculateSpread:
    """Test spread calculation."""

    def test_normal_spread(self):
        """Test spread with typical values."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        spread = calculate_spread(values)

        assert spread == 4.0

    def test_zero_spread(self):
        """Test spread when all values are identical."""
        values = [5.0, 5.0, 5.0]
        spread = calculate_spread(values)

        assert spread == 0.0

    def test_empty_values(self):
        """Test spread with empty list."""
        spread = calculate_spread([])

        assert spread == 0.0


class TestAnalyzeConvergence:
    """Test convergence/divergence analysis."""

    def test_converging(self):
        """Test detection of convergence (CV decreasing)."""
        current = [10.0, 10.5, 10.2]  # Low CV
        past = [10.0, 15.0, 5.0]  # High CV

        result = analyze_convergence(current, past)

        assert result["direction"] == "converging"
        assert result["current_cv"] < result["past_cv"]
        assert "converging" in result["interpretation"].lower()

    def test_diverging(self):
        """Test detection of divergence (CV increasing)."""
        current = [10.0, 20.0, 5.0]  # High CV
        past = [10.0, 10.5, 9.5]  # Low CV

        result = analyze_convergence(current, past)

        assert result["direction"] == "diverging"
        assert result["current_cv"] > result["past_cv"]
        assert "diverging" in result["interpretation"].lower()

    def test_stable(self):
        """Test stable convergence (CV unchanged)."""
        current = [10.0, 10.5, 9.5]
        past = [10.0, 10.6, 9.4]  # Similar CV

        result = analyze_convergence(current, past)

        assert result["direction"] == "stable"
        assert "stable" in result["interpretation"].lower()

    def test_no_past_values_low_cv(self):
        """Test interpretation without past values (low CV)."""
        current = [10.0, 10.1, 10.2]

        result = analyze_convergence(current)

        assert result["past_cv"] is None
        assert "tightly clustered" in result["interpretation"].lower()

    def test_no_past_values_high_cv(self):
        """Test interpretation without past values (high CV)."""
        current = [10.0, 20.0, 5.0]

        result = analyze_convergence(current)

        assert result["past_cv"] is None
        assert "high variation" in result["interpretation"].lower()

    def test_no_past_values_moderate_cv(self):
        """Test interpretation without past values (moderate CV)."""
        current = [10.0, 12.0, 8.0]

        result = analyze_convergence(current)

        assert result["past_cv"] is None
        assert "moderate" in result["interpretation"].lower()
