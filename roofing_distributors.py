import csv
import os

OUT = "/Users/tradbot/.openclaw/workspace/AF_Roofing_Distributors_Texas.csv"

distributors = [
    # AUSTIN
    ("Austin", "ABC Supply", "901 E St Johns Ave", "Austin", "TX", "78753", "(512) 454-0400", "www.abcsupply.com", "Jason Bludau (Mgr)"),
    ("Austin", "ABC Supply", "15508 Bratton Ln, Ste 100", "Austin", "TX", "78728", "", "www.abcsupply.com", ""),
    ("Austin", "ABC Supply", "4905 Winnebago Ln", "Austin", "TX", "78744", "", "www.abcsupply.com", ""),
    ("Austin", "L&W Supply", "503 Industrial Blvd", "Austin", "TX", "78745", "(512) 444-1804", "lwsupply.com", ""),
    ("Austin", "Beacon Building Products (QXO)", "Austin area", "", "TX", "", "", "locations.becn.com", ""),
    ("Austin", "SRS Building Products", "Austin", "", "TX", "", "", "srsdistribution.com", ""),
    ("Austin", "Roofing Supply Group", "8319 N Lamar Blvd", "Austin", "TX", "78753", "", "rsrooferssupply.com", ""),
    ("Austin", "Budget Roofing Supply", "Austin", "Austin", "TX", "", "", "budgetroofingsupply.com", ""),

    # BRYAN / COLLEGE STATION
    ("Bryan/College Station", "QXO (Beacon)", "4100 E State Hwy 21", "Bryan", "TX", "77808", "", "locations.becn.com", ""),
    ("Bryan/College Station", "SRS Building Products", "College Station", "", "TX", "", "", "srsdistribution.com", ""),
    ("Bryan/College Station", "Builders FirstSource", "College Station", "", "TX", "", "", "bldr.com", ""),
    ("Bryan/College Station", "McCoy's Building Supply", "Bryan", "", "TX", "", "", "mccoys.com", ""),

    # SAN ANTONIO
    ("San Antonio", "SRS Building Products", "San Antonio (Central)", "", "TX", "", "", "srsdistribution.com", ""),
    ("San Antonio", "L&W Supply", "7059 Pipestone Rd", "Schertz", "TX", "78154", "", "lwsupply.com", ""),
    ("San Antonio", "84 Lumber", "18100 Fm 2252", "San Antonio", "TX", "", "", "84lumber.com", ""),
    ("San Antonio", "84 Lumber", "327 Riverside Dr", "San Antonio", "TX", "", "", "84lumber.com", ""),
    ("San Antonio", "ABC Supply", "San Antonio area", "", "TX", "", "", "abcsupply.com", ""),
    ("San Antonio", "Texas Building Supply (US LBM)", "San Antonio region", "", "TX", "", "", "texasbuildingsupply.com", ""),
    ("San Antonio", "Elite Steel & Supply", "Serves San Antonio", "", "TX", "", "", "elitesteelandsupply.com", ""),

    # HOUSTON
    ("Houston", "SRS Building Products", "16409 Bratton Lane", "Houston", "TX", "78728", "", "srsdistribution.com", ""),
    ("Houston", "L&W Supply", "7901 Hansen Rd", "Houston", "TX", "77061", "(713) 462-0100", "lwsupply.com", ""),
    ("Houston", "L&W Supply", "1012 Rankin Rd", "Houston", "TX", "77092", "", "lwsupply.com", ""),
    ("Houston", "RSI Roofers Supply", "Houston", "", "TX", "", "", "rsirooferssupply.com", ""),
    ("Houston", "RGE Houston Roofing Supply", "Houston", "", "TX", "", "", "rgehoustonroofingsupply.com", ""),
    ("Houston", "Roofing Supply Inc", "Houston", "", "TX", "", "", "facebook.com/RoofingSupplyInc", ""),
    ("Houston", "84 Lumber", "22770 Northwest Fwy", "Houston", "TX", "", "", "84lumber.com", ""),
    ("Houston", "ABC Supply", "Houston (multiple locations)", "", "TX", "", "", "abcsupply.com", ""),
    ("Houston", "Beacon Building Products (QXO)", "Houston", "", "TX", "", "", "locations.becn.com", ""),
    ("Houston", "QXO Commercial", "Houston", "", "TX", "", "", "qxo.com", ""),

    # WACO / CENTRAL TEXAS
    ("Waco/Central TX", "Gross Yowell", "2201 Franklin Ave", "Waco", "TX", "76701", "", "grossyowell.com", ""),
    ("Waco/Central TX", "L&W Supply", "715 Jewell Dr", "Waco", "TX", "", "", "lwsupply.com", ""),
    ("Waco/Central TX", "Cowtown Materials", "Waco — serves Temple, Killeen, Bryan", "", "TX", "", "", "cowtownmaterials.com", ""),
    ("Waco/Central TX", "SRS Building Products", "Waco", "", "TX", "", "", "srsdistribution.com", ""),
    ("Waco/Central TX", "Beacon Building Products (QXO)", "Waco area", "", "TX", "", "", "locations.becn.com", ""),

    # BROADER TEXAS
    ("Multi-Region", "ABC Supply", "Temple — serves Austin corridor", "Temple", "TX", "", "", "abcsupply.com", ""),
    ("Multi-Region", "Mid-South Roofing Supply", "Texas operations", "", "TX", "", "", "midsouthroofing.com", ""),
    ("Multi-Region", "Carolina Atlantic", "Texas wholesale residential/commercial", "", "TX", "", "", "carolinaatlantic.com", ""),
    ("Multi-Region", "Texas Building Supply (JP Hart, Arrowhead)", "Statewide", "", "TX", "", "", "texasbuildingsupply.com", ""),
    ("Multi-Region", "SRS Distribution", "Statewide — Houston, Austin, SA, College Station", "", "TX", "", "", "srsdistribution.com", ""),
    ("Multi-Region", "Elite Steel & Supply", "Waco, Austin, San Antonio", "", "TX", "", "", "elitesteelandsupply.com", ""),
]

# Add more based on SRS locations
srs_additional = [
    ("Houston", "SRS Building Products", "1854 E Beltline Rd #3", "Coppell", "TX", "75019", "", "srsdistribution.com", ""),
    ("Houston", "SRS Building Products", "13315 Theis Lane", "Tomball", "TX", "77375", "", "srsdistribution.com", ""),
    ("Bryan/College Station", "SRS Building Products", "Serves Bryan-College Station", "", "TX", "", "", "srsdistribution.com", ""),
]

distributors += srs_additional

# Write CSV
with open(OUT, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Region", "Company", "Street Address", "City", "State", "Zip", "Phone", "Website", "GM / Contact", "Notes"])
    for d in distributors:
        writer.writerow(d)

print(f"CSV written: {OUT}  ({len(distributors)} rows)")
