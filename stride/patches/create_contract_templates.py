import frappe

TEMPLATES = [
	{
		"template_name": "Renting Agreement (English)",
		"template_type": "Renting Agreement",
		"is_default": 1,
		"content": """
<div style="font-family: Arial, sans-serif; font-size: 13px; line-height: 1.6;">

<h2 style="text-align: center;">VEHICLE RENTING AGREEMENT</h2>

<p>This Vehicle Renting Agreement ("<strong>Agreement</strong>") is entered into on
<strong>{{ today }}</strong> by and between:</p>

<h4>1. PARTIES</h4>
<p><strong>Vehicle Owner ("Owner"):</strong> {{ company }}<br/>
<strong>Customer ("Renter"):</strong> {{ customer_name }}<br/>
<strong>Identification Type:</strong> {{ customer_identification_type }}<br/>
<strong>Identification No:</strong> {{ customer_identification_no }}<br/>
<strong>Contact:</strong> {{ customer_contact or '' }}</p>

<h4>2. GUARANTOR</h4>
<p><strong>Full Name:</strong> {{ guarantor_name }}<br/>
<strong>National ID No:</strong> {{ guarantor_id_no }}<br/>
<strong>Contact:</strong> {{ guarantor_contact or '' }}</p>

<h4>3. VEHICLE DETAILS</h4>
<p><strong>Vehicle:</strong> {{ vehicle }} — {{ vehicle_name }}</p>

<h4>4. RENTAL TERMS</h4>
<p><strong>Rate:</strong> {{ rate }} per {{ period_type }}<br/>
<strong>Duration:</strong> {{ duration }}<br/>
<strong>Start Date:</strong> {{ start_date or 'To be determined' }}<br/>
<strong>End Date:</strong> {{ end_date or 'To be determined' }}<br/>
<strong>Total Amount:</strong> {{ total_amount }}</p>

{% if rent_to_own %}
<p><strong>Rent-to-Own:</strong> Upon successful completion of all payments, ownership
of the vehicle shall be transferred to the Renter.</p>
{% endif %}

<h4>5. PAYMENT OBLIGATIONS</h4>
<p>The Renter shall pay the agreed rental amount on or before each due date as per
the payment schedule generated under the Lease. Late payments may attract penalties
as determined by the Owner.</p>

<h4>6. GPS TRACKING CONSENT</h4>
<p>The Renter acknowledges and consents that the Vehicle is equipped with a GPS
tracking device for security and safety purposes. The Owner reserves the right
to monitor the Vehicle's location at all times during the rental period.</p>

<h4>7. VEHICLE CARE & MAINTENANCE</h4>
<p>The Renter shall maintain the Vehicle in good condition and shall be responsible
for routine maintenance costs during the rental period. Any damage beyond normal
wear and tear shall be borne by the Renter.</p>

<h4>8. TERMINATION</h4>
<p>Either party may terminate this Agreement with 30 days written notice. Upon
termination, the Renter shall return the Vehicle in the condition received,
subject to reasonable wear and tear. Any outstanding payments shall remain due.</p>

<h4>9. GOVERNING LAW</h4>
<p>This Agreement shall be governed by the laws of the United Republic of Tanzania.</p>

<br/>
<table style="width:100%; border:none;">
<tr>
<td style="width:50%; border:none;">
<p><strong>Owner Signature:</strong></p>
<br/><br/>
<p>____________________________</p>
<p>Name: ________________________</p>
<p>Date: ________________________</p>
</td>
<td style="width:50%; border:none;">
<p><strong>Renter Signature:</strong></p>
<br/><br/>
<p>____________________________</p>
<p>Name: {{ customer_name }}</p>
<p>Date: ________________________</p>
</td>
</tr>
<tr>
<td colspan="2" style="border:none; padding-top: 20px;">
<p><strong>Guarantor Signature:</strong></p>
<br/><br/>
<p>____________________________</p>
<p>Name: {{ guarantor_name }}</p>
<p>ID No: {{ guarantor_id_no }}</p>
<p>Date: ________________________</p>
</td>
</tr>
</table>

</div>
""",
	},
	{
		"template_name": "Renting Agreement (Swahili)",
		"template_type": "Renting Agreement",
		"is_default": 0,
		"content": """
<div style="font-family: Arial, sans-serif; font-size: 13px; line-height: 1.6;">

<h2 style="text-align: center;">MKATABA WA KUKODISHA GARI</h2>

<p>Mkataba huu wa Kukodisha Gari ("<strong>Mkataba</strong>") umeingiwa tarehe
<strong>{{ today }}</strong> kati ya:</p>

<h4>1. WAHUSIKA</h4>
<p><strong>Mmiliki wa Gari ("Mmiliki"):</strong> {{ company }}<br/>
<strong>Mteja ("Mkodishaji"):</strong> {{ customer_name }}<br/>
<strong>Aina ya Kitambulisho:</strong> {{ customer_identification_type }}<br/>
<strong>Namba ya Kitambulisho:</strong> {{ customer_identification_no }}<br/>
<strong>Mawasiliano:</strong> {{ customer_contact or '' }}</p>

<h4>2. MDHAMINI</h4>
<p><strong>Jina Kamili:</strong> {{ guarantor_name }}<br/>
<strong>Namba ya Kitambulisho cha Taifa:</strong> {{ guarantor_id_no }}<br/>
<strong>Mawasiliano:</strong> {{ guarantor_contact or '' }}</p>

<h4>3. MAELEZO YA GARI</h4>
<p><strong>Gari:</strong> {{ vehicle }} — {{ vehicle_name }}</p>

<h4>4. MASHARTI YA KUKODISHA</h4>
<p><strong>Kiwango:</strong> {{ rate }} kwa {{ period_type }}<br/>
<strong>Muda:</strong> {{ duration }}<br/>
<strong>Tarehe ya Kuanza:</strong> {{ start_date or 'Itaamuliwa' }}<br/>
<strong>Tarehe ya Mwisho:</strong> {{ end_date or 'Itaamuliwa' }}<br/>
<strong>Jumla ya Kiasi:</strong> {{ total_amount }}</p>

{% if rent_to_own %}
<p><strong>Kodisha-Kisha-Miliki:</strong> Baada ya malipo yote kukamilika,
umiliki wa gari utahamishiwa kwa Mkodishaji.</p>
{% endif %}

<h4>5. WAJIBU WA MALIPO</h4>
<p>Mkodishaji atalipa kiasi kilichokubaliwa cha kodi kabla au siku ya tarehe
ya malipo kulingana na ratiba ya malipo iliyoandaliwa chini ya Mkataba wa Kodi.
Malipo ya kuchelewa yanaweza kupata adhabu kama itakavyoamuliwa na Mmiliki.</p>

<h4>6. KIBALI CHA UFUATILIAJI WA GPS</h4>
<p>Mkodishaji anakubali na kukubaliana kuwa Gari limewekwa kifaa cha ufuatiliaji
wa GPS kwa madhumuni ya usalama. Mmiliki ana haki ya kufuatilia eneo la Gari
wakati wote wa kipindi cha kukodisha.</p>

<h4>7. UTUNZAJI NA MATENGENEZO YA GARI</h4>
<p>Mkodishaji atatunza Gari katika hali nzuri na atawajibika kwa gharama za
matengenezo ya kawaida wakati wa kipindi cha kukodisha. Uharibifu wowote zaidi
ya uchakavu wa kawaida utabebwa na Mkodishaji.</p>

<h4>8. KUSITISHWA</h4>
<p>Mhusika yeyote anaweza kusitisha Mkataba huu kwa notisi ya maandishi ya
siku 30. Mkodishaji atarudisha Gari katika hali aliyoipokea. Malipo yoyote
ambayo hayajalipwa yatabaki kuwa deni.</p>

<h4>9. SHERIA INAYOTUMIKA</h4>
<p>Mkataba huu utatawaliwa na sheria za Jamhuri ya Muungano wa Tanzania.</p>

<br/>
<table style="width:100%; border:none;">
<tr>
<td style="width:50%; border:none;">
<p><strong>Sahihi ya Mmiliki:</strong></p>
<br/><br/>
<p>____________________________</p>
<p>Jina: ________________________</p>
<p>Tarehe: ________________________</p>
</td>
<td style="width:50%; border:none;">
<p><strong>Sahihi ya Mkodishaji:</strong></p>
<br/><br/>
<p>____________________________</p>
<p>Jina: {{ customer_name }}</p>
<p>Tarehe: ________________________</p>
</td>
</tr>
<tr>
<td colspan="2" style="border:none; padding-top: 20px;">
<p><strong>Sahihi ya Mdhamini:</strong></p>
<br/><br/>
<p>____________________________</p>
<p>Jina: {{ guarantor_name }}</p>
<p>Kitambulisho: {{ guarantor_id_no }}</p>
<p>Tarehe: ________________________</p>
</td>
</tr>
</table>

</div>
""",
	},
	{
		"template_name": "Vehicle Handover (English)",
		"template_type": "Vehicle Handover",
		"is_default": 1,
		"content": """
<div style="font-family: Arial, sans-serif; font-size: 13px; line-height: 1.6;">

<h2 style="text-align: center;">VEHICLE HANDOVER CERTIFICATE</h2>

<p>This Vehicle Handover Certificate ("<strong>Certificate</strong>") is issued on
<strong>{{ today }}</strong> to confirm the transfer of vehicle ownership.</p>

<h4>1. PARTIES</h4>
<p><strong>Previous Owner ("Owner"):</strong> {{ company }}<br/>
<strong>New Owner ("Buyer"):</strong> {{ customer_name }}<br/>
<strong>Identification Type:</strong> {{ customer_identification_type }}<br/>
<strong>Identification No:</strong> {{ customer_identification_no }}</p>

<h4>2. GUARANTOR</h4>
<p><strong>Full Name:</strong> {{ guarantor_name }}<br/>
<strong>National ID No:</strong> {{ guarantor_id_no }}</p>

<h4>3. VEHICLE DETAILS</h4>
<p><strong>Vehicle:</strong> {{ vehicle }} — {{ vehicle_name }}</p>

<h4>4. HANDOVER DETAILS</h4>
<p><strong>Handover Date:</strong> {{ handover_date }}<br/>
<strong>Vehicle Condition:</strong> {{ vehicle_condition }}<br/>
<strong>Odometer Reading:</strong> {{ odometer_reading }} km</p>

{% if inspection_notes %}
<p><strong>Inspection Notes:</strong> {{ inspection_notes }}</p>
{% endif %}

<h4>5. PAYMENT CONFIRMATION</h4>
<p>The Owner hereby confirms that all rental payments under Rental Contract
<strong>{{ rental_contract }}</strong> and Lease <strong>{{ lease }}</strong>
have been received in full. The total amount of <strong>{{ total_amount }}</strong>
has been settled.</p>

<h4>6. TRANSFER OF OWNERSHIP</h4>
<p>The Owner hereby transfers full ownership of the above-described vehicle to the
Buyer, free and clear of all liens and encumbrances. The Buyer accepts the vehicle
in its current condition as described above.</p>

<h4>7. GPS DEVICE</h4>
<p>The GPS tracking device installed on the vehicle shall be removed or deactivated
upon completion of ownership transfer, unless otherwise agreed by both parties.</p>

<br/>
<table style="width:100%; border:none;">
<tr>
<td style="width:50%; border:none;">
<p><strong>Previous Owner Signature:</strong></p>
<br/><br/>
<p>____________________________</p>
<p>Name: ________________________</p>
<p>Date: ________________________</p>
</td>
<td style="width:50%; border:none;">
<p><strong>New Owner Signature:</strong></p>
<br/><br/>
<p>____________________________</p>
<p>Name: {{ customer_name }}</p>
<p>Date: ________________________</p>
</td>
</tr>
</table>

</div>
""",
	},
	{
		"template_name": "Vehicle Handover (Swahili)",
		"template_type": "Vehicle Handover",
		"is_default": 0,
		"content": """
<div style="font-family: Arial, sans-serif; font-size: 13px; line-height: 1.6;">

<h2 style="text-align: center;">HATI YA KUKABIDHIWA GARI</h2>

<p>Hati hii ya Kukabidhiwa Gari ("<strong>Hati</strong>") imetolewa tarehe
<strong>{{ today }}</strong> kuthibitisha uhamishaji wa umiliki wa gari.</p>

<h4>1. WAHUSIKA</h4>
<p><strong>Mmiliki wa Awali ("Mmiliki"):</strong> {{ company }}<br/>
<strong>Mmiliki Mpya ("Mnunuzi"):</strong> {{ customer_name }}<br/>
<strong>Aina ya Kitambulisho:</strong> {{ customer_identification_type }}<br/>
<strong>Namba ya Kitambulisho:</strong> {{ customer_identification_no }}</p>

<h4>2. MDHAMINI</h4>
<p><strong>Jina Kamili:</strong> {{ guarantor_name }}<br/>
<strong>Namba ya Kitambulisho cha Taifa:</strong> {{ guarantor_id_no }}</p>

<h4>3. MAELEZO YA GARI</h4>
<p><strong>Gari:</strong> {{ vehicle }} — {{ vehicle_name }}</p>

<h4>4. MAELEZO YA UKABIDHISHAJI</h4>
<p><strong>Tarehe ya Ukabidhishaji:</strong> {{ handover_date }}<br/>
<strong>Hali ya Gari:</strong> {{ vehicle_condition }}<br/>
<strong>Usomaji wa Odometer:</strong> {{ odometer_reading }} km</p>

{% if inspection_notes %}
<p><strong>Maelezo ya Ukaguzi:</strong> {{ inspection_notes }}</p>
{% endif %}

<h4>5. UTHIBITISHO WA MALIPO</h4>
<p>Mmiliki anathibitisha kuwa malipo yote ya kukodisha chini ya Mkataba wa
Kukodisha <strong>{{ rental_contract }}</strong> na Kodi <strong>{{ lease }}</strong>
yamepokelewa kikamilifu. Jumla ya kiasi cha <strong>{{ total_amount }}</strong>
kimelipwa.</p>

<h4>6. UHAMISHAJI WA UMILIKI</h4>
<p>Mmiliki anahamisha umiliki kamili wa gari lililotajwa hapo juu kwa Mnunuzi,
bila madeni yoyote. Mnunuzi anakubali gari katika hali yake ya sasa kama
ilivyoelezwa hapo juu.</p>

<h4>7. KIFAA CHA GPS</h4>
<p>Kifaa cha ufuatiliaji wa GPS kilichowekwa kwenye gari kitaondolewa au
kuzimwa baada ya uhamishaji wa umiliki kukamilika, isipokuwa kama wahusika
wote watakubaliana vinginevyo.</p>

<br/>
<table style="width:100%; border:none;">
<tr>
<td style="width:50%; border:none;">
<p><strong>Sahihi ya Mmiliki wa Awali:</strong></p>
<br/><br/>
<p>____________________________</p>
<p>Jina: ________________________</p>
<p>Tarehe: ________________________</p>
</td>
<td style="width:50%; border:none;">
<p><strong>Sahihi ya Mmiliki Mpya:</strong></p>
<br/><br/>
<p>____________________________</p>
<p>Jina: {{ customer_name }}</p>
<p>Tarehe: ________________________</p>
</td>
</tr>
</table>

</div>
""",
	},
]


def execute() -> None:
	"""Create default Contract Template records if they do not already exist."""
	for template_data in TEMPLATES:
		template_name = template_data["template_name"]
		if frappe.db.exists("Contract Template", template_name):
			continue

		doc = frappe.new_doc("Contract Template")
		doc.update(template_data)
		doc.insert(ignore_permissions=True)

	frappe.db.commit()
