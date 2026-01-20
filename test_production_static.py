"""
CRITICAL: Test if production static files are accessible

Visit these URLs directly in browser:
"""

print("=== PRODUCTION STATIC FILE TESTS ===\n")

# Test 1: Static file serving (general)
print("1. Test CSS file:")
print("   https://vn-travel.onrender.com/static/css/custom.css")
print("   Expected: CSS file downloads/displays\n")

# Test 2: Static image (fallback images we know exist)
print("2. Test static image:")
print("   https://vn-travel.onrender.com/static/images/ha_long_bay.png")
print("   Expected: Image displays\n")

# Test 3: Media folder (tour images)
print("3. Test tour image (should be in staticfiles/media/tours/):")
print("   https://vn-travel.onrender.com/static/media/tours/tour_7_ha_noi_ha_long_tour_1768394623908_HOTLBzT.png")
print("   Expected: Image displays")
print("   If 404: Files not in staticfiles or WhiteNoise not serving\n")

# Test 4: Check if DEBUG is False
print("4. Check Django settings:")
print("   https://vn-travel.onrender.com/health/")
print("   Check response - if shows detailed errors, DEBUG=True (BAD!)\n")

print("=== INSTRUCTIONS ===")
print("1. Open each URL above in browser")
print("2. Report which ones work (✅) and which fail (❌)")
print("3. Screenshot any errors")
print("\nBased on results, I'll implement the RIGHT fix!")
