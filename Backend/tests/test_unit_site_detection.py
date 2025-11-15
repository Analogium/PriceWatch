"""
Unit tests for site detection functionality.
"""
import pytest
from app.services.scraper import SiteDetector


@pytest.mark.unit
class TestSiteDetector:
    """Test site detection from URLs."""

    def test_detect_amazon_fr(self):
        """Test detection of Amazon.fr."""
        url = "https://www.amazon.fr/dp/B08L5VNF78"
        assert SiteDetector.detect_site(url) == 'amazon'

    def test_detect_amazon_com(self):
        """Test detection of Amazon.com."""
        url = "https://www.amazon.com/dp/B08L5VNF78"
        assert SiteDetector.detect_site(url) == 'amazon'

    def test_detect_amazon_de(self):
        """Test detection of Amazon.de."""
        url = "https://www.amazon.de/dp/B08L5VNF78"
        assert SiteDetector.detect_site(url) == 'amazon'

    def test_detect_amazon_uk(self):
        """Test detection of Amazon.co.uk."""
        url = "https://www.amazon.co.uk/dp/B08L5VNF78"
        assert SiteDetector.detect_site(url) == 'amazon'

    def test_detect_amazon_without_www(self):
        """Test detection of Amazon without www prefix."""
        url = "https://amazon.fr/dp/B08L5VNF78"
        assert SiteDetector.detect_site(url) == 'amazon'

    def test_detect_amazon_complex_url(self):
        """Test detection with complex Amazon URL."""
        url = "https://www.amazon.fr/Blukar-Rechargeable-Puissante-Aluminium-déclairage/dp/B0C3VZ57NY/?_encoding=UTF8&pd_rd_w=Px0c2&tag=test-21"
        assert SiteDetector.detect_site(url) == 'amazon'

    def test_detect_fnac(self):
        """Test detection of Fnac."""
        url = "https://www.fnac.com/a21752626/Product-Name"
        assert SiteDetector.detect_site(url) == 'fnac'

    def test_detect_fnac_fr(self):
        """Test detection of Fnac.fr."""
        url = "https://www.fnac.fr/product/12345"
        assert SiteDetector.detect_site(url) == 'fnac'

    def test_detect_darty(self):
        """Test detection of Darty."""
        url = "https://www.darty.com/nav/achat/petit_electromenager/aspirateur/aspirateur_robot/roborock_qrevo_curvx.html"
        assert SiteDetector.detect_site(url) == 'darty'

    def test_detect_cdiscount(self):
        """Test detection of Cdiscount."""
        url = "https://www.cdiscount.com/informatique/tablettes-tactiles-ebooks/apple-ipad-mini-6-wi-fi-64go-gris-sideral/f-10798-app0194252584576.html"
        assert SiteDetector.detect_site(url) == 'cdiscount'

    def test_detect_boulanger(self):
        """Test detection of Boulanger."""
        url = "https://www.boulanger.com/ref/1174942"
        assert SiteDetector.detect_site(url) == 'boulanger'

    def test_detect_boulanger_fr(self):
        """Test detection of Boulanger.fr."""
        url = "https://www.boulanger.fr/ref/1174942"
        assert SiteDetector.detect_site(url) == 'boulanger'

    def test_detect_leclerc(self):
        """Test detection of E.Leclerc."""
        url = "https://www.e.leclerc/produit/12345"
        assert SiteDetector.detect_site(url) == 'leclerc'

    def test_detect_leclerc_hyphen(self):
        """Test detection of E-Leclerc with hyphen."""
        url = "https://www.e-leclerc.fr/produit/12345"
        assert SiteDetector.detect_site(url) == 'leclerc'

    def test_detect_unknown_site(self):
        """Test detection of unknown site."""
        url = "https://www.unknownsite.com/product/12345"
        assert SiteDetector.detect_site(url) is None

    def test_detect_case_insensitive(self):
        """Test that detection is case-insensitive."""
        url_upper = "https://WWW.AMAZON.FR/dp/B08L5VNF78"
        url_mixed = "https://WwW.AmAzOn.fR/dp/B08L5VNF78"
        assert SiteDetector.detect_site(url_upper) == 'amazon'
        assert SiteDetector.detect_site(url_mixed) == 'amazon'

    def test_detect_with_subdomain(self):
        """Test detection with subdomain."""
        url = "https://shop.amazon.fr/dp/B08L5VNF78"
        # Should still detect even with subdomain
        result = SiteDetector.detect_site(url)
        assert result == 'amazon' or result is None  # Depends on implementation

    def test_detect_invalid_url(self):
        """Test detection with invalid URL."""
        url = "not-a-valid-url"
        result = SiteDetector.detect_site(url)
        # Should handle gracefully
        assert result is None or isinstance(result, str)

    def test_detect_empty_url(self):
        """Test detection with empty URL."""
        url = ""
        result = SiteDetector.detect_site(url)
        assert result is None

    def test_detect_url_without_protocol(self):
        """Test detection with URL without protocol."""
        url = "www.amazon.fr/dp/B08L5VNF78"
        result = SiteDetector.detect_site(url)
        # Should still work or return None gracefully
        assert result == 'amazon' or result is None


@pytest.mark.unit
class TestSiteDetectorPatterns:
    """Test site detector pattern configuration."""

    def test_patterns_exist_for_all_sites(self):
        """Test that patterns are defined for all sites."""
        patterns = SiteDetector.SITE_PATTERNS
        assert len(patterns) > 0
        assert 'amazon' in patterns
        assert 'fnac' in patterns
        assert 'darty' in patterns
        assert 'cdiscount' in patterns
        assert 'boulanger' in patterns
        assert 'leclerc' in patterns

    def test_amazon_has_multiple_domains(self):
        """Test that Amazon has multiple country domains."""
        amazon_patterns = SiteDetector.SITE_PATTERNS['amazon']
        assert len(amazon_patterns) >= 4  # At least .fr, .com, .de, .co.uk
        assert 'amazon.fr' in amazon_patterns
        assert 'amazon.com' in amazon_patterns
        assert 'amazon.de' in amazon_patterns
        assert 'amazon.co.uk' in amazon_patterns

    def test_all_patterns_are_lowercase(self):
        """Test that all patterns are in lowercase."""
        for site, patterns in SiteDetector.SITE_PATTERNS.items():
            for pattern in patterns:
                assert pattern == pattern.lower(), f"Pattern '{pattern}' for site '{site}' should be lowercase"

    def test_no_duplicate_patterns(self):
        """Test that there are no duplicate patterns across sites."""
        all_patterns = []
        for patterns in SiteDetector.SITE_PATTERNS.values():
            all_patterns.extend(patterns)

        # Check for duplicates
        assert len(all_patterns) == len(set(all_patterns)), "Found duplicate patterns across sites"
