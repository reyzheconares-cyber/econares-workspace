# Mindanao Lead Enrichment - PowerShell COM script
# Apr 22 2026 - Updates MASTER sheet in-place
# Pattern: backup -> audit -> patch per row -> verify

$XLSX_PATH = "G:\My Drive\02 Areas\Reports\ECONARES SALES and MARKETING UPDATES-RZH - Jun. DAILY intel.xlsx"
$BACKUP_PATH = "G:\My Drive\02 Areas\Reports\ECONARES SALES and MARKETING UPDATES-RZH - Jun.PRE-MINDANAO-ENRICHMENT-20260622.xlsx"

# 1. Backup
Copy-Item $XLSX_PATH $BACKUP_PATH -Force
Write-Host "[1/4] Backup created: $BACKUP_PATH" -ForegroundColor Cyan

# 2. Open Excel
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$wb = $excel.Workbooks.Open($XLSX_PATH)
$ws = $wb.Sheets("MASTER")
Write-Host "[2/4] Opened XLSX: $XLSX_PATH" -ForegroundColor Cyan

# 3. Define updates - (row, col, newValue, description)
# 3a. L1 (MASTER!156) - Republic Cement - region fix + person + remarks
$updates = @(
    # L1: Republic Cement (MASTER!156) - Region fix + person + remarks
    @{Row=156; Col=5;  Value="Mindanao";                                    Desc="L1: Region fix Visayas->Mindanao (RCMI Iligan)"},
    @{Row=156; Col=6;  Value="Republic Cement Services Procurement Team - Allan Saquilayan (RCSI) / Rey Floresca (former)"; Desc="L1: Person update - remove wrong Taiheiyo contact"},
    @{Row=156; Col=9;  Value="HQ: 15F Menarco Tower, 32nd St., BGC, Taguig City 1632; Plant: Kiwalan, Iligan City, Lanao del Norte"; Desc="L1: Add Iligan plant address"},
    @{Row=156; Col=15; Value="05/12/2026: Ffup email sent`n05/05/20262: Forwarded to Rachel from Allan. Sent in`nFLAG Jun 2026: RCMI is the Iligan plant (Northern Mindanao). Previous contact Rodulfo Yase was Taiheiyo PH (wrong-row). Procurement via RCSI shared services. Named contacts via LinkedIn: Allan Saquilayan (RCSI), Rey Floresca (ex-RCSI 2017-2023, now Ash Grove). Plant address: Kiwalan, Iligan City, Lanao del Norte."; Desc="L1: KYC note appended"},

    # L2: Holcim Cebu Warehouse (MASTER!152) - actually Lugait plant
    @{Row=152; Col=2;  Value="Holcim Philippines Inc. - Lugait Plant";     Desc="L2: Company name fix - this is the Lugait plant, not the Cebu warehouse"},
    @{Row=152; Col=5;  Value="Mindanao";                                    Desc="L2: Region fix Visayas->Mindanao (Lugait, Misamis Oriental)"},
    @{Row=152; Col=6;  Value="Luningning Donato (Lugait Plant Head, 2024); HPH Shared Services Procurement (Ronaldo Jimeno ex-HPH, now Eagle Cement)"; Desc="L2: Person update"},
    @{Row=152; Col=9;  Value="Plant: Lugait, Misamis Oriental, Northern Mindanao 9001"; Desc="L2: Plant address"},
    @{Row=152; Col=15; Value="FLAG Jun 2026: This is Holcim Philippines Lugait Plant (Mindanao), not the Cebu warehouse. Region fix from Visayas. Plant Head: Luningning Donato (2024 appointment). Procurement via HPH Shared Services. ex-HPH Procurement Manager: Ronaldo Jimeno (now Eagle Cement 2017+). Email info@lafargeholcim.com.ph is legacy pre-rebrand - current domain is @holcim.ph. Parent: Holcim Group (Swiss)."; Desc="L2: KYC note"},

    # L11: SPi Power (MASTER!116) - SPI case fix + region fix + AboitizPower procurement
    @{Row=116; Col=2;  Value="SPI Power Inc.";                              Desc="L11: Case fix SPi->SPI per official company name"},
    @{Row=116; Col=5;  Value="Mindanao";                                    Desc="L11: Region fix Visayas->Mindanao (Villanueva, Misamis Oriental)"},
    @{Row=116; Col=6;  Value="AboitizPower Thermal Procurement - Rhoda Cruz (CPO); SPI plant-level TBD"; Desc="L11: Plant-level person TBD, parent procurement via Rhoda Cruz"},
    @{Row=116; Col=7;  Value="(032) 230 8200";                              Desc="L11: Phone kept as AboitizPower regional contact"},
    @{Row=116; Col=15; Value="FLAG Jun 2026: SPi case fix to SPI. Region fix Villanueva = Misamis Oriental = Mindanao. AboitizPower acquired 85% via SPI Power Inc. in 2022. Plant-level decision-maker NOT publicly published - KEEP TBD. Procurement routes to AboitizPower Thermal Group (Rhoda Cruz, CPO, info@aboitizpower.com)."; Desc="L11: KYC note"},

    # L14: Sarangani Energy (MASTER!107) - region fix + Meralco PowerGen routing
    @{Row=107; Col=5;  Value="Mindanao";                                    Desc="L14: Region fix Visayas->Mindanao (Maasim, Sarangani)"},
    @{Row=107; Col=6;  Value="Meralco PowerGen / GBP Procurement - support@globalpower.com.ph; ATEC corporate; Toyota Tsusho JV partner"; Desc="L14: Person update - route via parent group"},
    @{Row=107; Col=8;  Value="support@globalpower.com.ph";                  Desc="L14: Email - Meralco PowerGen / GBP parent (existing master contact)"},
    @{Row=107; Col=15; Value="FLAG Jun 2026: Region fix Maasim = Sarangani = SOCCSKSARGEN = Mindanao. Ownership: ATEC 75% (parent: ACR 50% + GBP 50%) + Toyota Tsusho 25%. 237 MW CFB. Procurement routes through Meralco PowerGen / GBP (mgmt partner) per existing master contact support@globalpower.com.ph. Plant HQ: National Hwy, Brgy Kamanga, Maasim 9502 Sarangani. (632) 8823 7225 = Meralco PowerGen corporate."; Desc="L14: KYC note"}
)

# Apply existing-row updates
foreach ($u in $updates) {
    $cell = $ws.Cells.Item($u.Row, $u.Col)
    $cell.Value = $u.Value
    Write-Host "  MASTER!$($u.Row) col $($u.Col) [$($u.Desc)]" -ForegroundColor Yellow
}

# 3b. Add 3 new rows for L12, L13, L16
# Find next empty row in MASTER
$lastRow = $ws.UsedRange.Rows.Count
Write-Host "  Current last row in MASTER: $lastRow" -ForegroundColor Yellow

# Get max "No" (col A) to renumber
$maxNo = 0
for ($r = 2; $r -le $lastRow; $r++) {
    $v = $ws.Cells.Item($r, 1).Value
    if ($v -is [int] -or $v -is [double]) { if ([int]$v -gt $maxNo) { $maxNo = [int]$v } }
}
Write-Host "  Max 'No' value: $maxNo" -ForegroundColor Yellow

# Add new rows
$nextRow = $lastRow + 1
$newRows = @(
    @{
        # L12: FDC Misamis
        No        = $maxNo + 1
        Company   = "FDC Misamis Power Corporation"
        Commodity = "Coal/Power"
        Industry  = "Power Generation"
        Region    = "Mindanao"
        Person    = "Mr. Roderick Fernandez (FDCUI Taguig - Procurement); FDC SVP Head: Juan Eugenio Roxas"
        Phone     = "+632 575.1600 / +632 819.6131"
        Email     = "Contact TBD - needs research"
        Address   = "Plant: PHIVIDEC Industrial Estate, Villanueva, Misamis Oriental 9001; HQ: Unit D, 11F Cyber Sigma, Lawton Ave, McKinley West, Taguig City 1630"
        Remarks   = "Jun 2026: NEW Mindanao lead per RZH. 405 MW CFB (3x135MW), commissioned Sep 2016. Coal demand ~500k MT/yr, 80% Indonesia / 20% local. Parent: FDCUI / Filinvest Development Corporation. Procurement via FDCUI Taguig HQ. Roderick Fernandez contact per 2021 EIA filing."
    },
    @{
        # L13: Therma South
        No        = $maxNo + 2
        Company   = "Therma South, Inc. (TSI)"
        Commodity = "Coal/Power"
        Industry  = "Power Generation"
        Region    = "Mindanao"
        Person    = "JP Pantino (TSI Facility Head, 2024); Procurement via AboitizPower Thermal - Rhoda Cruz (CPO)"
        Phone     = "(63-82) 244-6500"
        Email     = "info@aboitizpower.com"
        Address   = "Binugao, Toril, Davao City / Sta. Cruz, Davao del Sur"
        Remarks   = "Jun 2026: NEW Mindanao lead per RZH. 300 MW CFB (2x150MW), commissioned Sep 2015 / Feb 2016. Coal demand 1.0-1.2 MT/yr, Indonesia-sourced, sulfur cap 1% (per World Coal 2013 EPC loan disclosure). Facility Head: JP Pantino. Parent: AboitizPower Corp."
    },
    @{
        # L16: San Ramon Power
        No        = $maxNo + 3
        Company   = "San Ramon Power Inc. (SRPI)"
        Commodity = "Coal/Power"
        Industry  = "Power Generation"
        Region    = "Mindanao"
        Person    = "Engr. Archimedes Donato (SRPI Project Manager); Joseph C. Nocos (ACR Power Group VP Business Dev)"
        Phone     = "Contact TBD - needs research"
        Email     = "Contact TBD - needs research"
        Address   = "Talisayan, Zamboanga City, Western Mindanao"
        Remarks   = "Jun 2026: NEW Mindanao lead per RZH. 120 MW subcritical CFB, pre-construction, target COD 2027-2028 (delayed from 2023). EPC shortlisted: NEPC + SEPCO III. Coal supply RFP will follow EPC finalization. Owner: ATEC (ACR 50% + Meralco 50%). Forward demand ~400-500k MT/yr. Project Manager: Engr. Archimedes Donato."
    }
)

foreach ($nr in $newRows) {
    $ws.Cells.Item($nextRow, 1).Value  = $nr.No
    $ws.Cells.Item($nextRow, 2).Value  = $nr.Company
    $ws.Cells.Item($nextRow, 3).Value  = $nr.Commodity
    $ws.Cells.Item($nextRow, 4).Value  = $nr.Industry
    $ws.Cells.Item($nextRow, 5).Value  = $nr.Region
    $ws.Cells.Item($nextRow, 6).Value  = $nr.Person
    $ws.Cells.Item($nextRow, 7).Value  = $nr.Phone
    $ws.Cells.Item($nextRow, 8).Value  = $nr.Email
    $ws.Cells.Item($nextRow, 9).Value  = $nr.Address
    $ws.Cells.Item($nextRow, 15).Value = $nr.Remarks
    Write-Host "  NEW row $nextRow : $($nr.Company)" -ForegroundColor Green
    $nextRow++
}

# 4. Save and close
$wb.Save()
$wb.Close()
$excel.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null

Write-Host "[4/4] Saved & closed. 3 new rows + 4 region fixes + 4 contact enrichments applied." -ForegroundColor Green
Write-Host "Backup: $BACKUP_PATH" -ForegroundColor Cyan
