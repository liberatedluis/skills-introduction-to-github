"""300 most-spoken living languages, ranked by approximate total speakers."""

# rank|iso639-3|english|native|speakers_millions|script|rtl|region
SEED = """
1|eng|English|English|1490|Latn|0|Worldwide
2|cmn|Mandarin Chinese|普通话|1180|Hans|0|East Asia
3|hin|Hindi|हिन्दी|611|Deva|0|South Asia
4|spa|Spanish|Español|561|Latn|0|Worldwide
5|arb|Standard Arabic|العربية الفصحى|335|Arab|1|MENA
6|fra|French|Français|334|Latn|0|Worldwide
7|ben|Bengali|বাংলা|274|Beng|0|South Asia
8|por|Portuguese|Português|269|Latn|0|Worldwide
9|ind|Indonesian|Bahasa Indonesia|255|Latn|0|Southeast Asia
10|urd|Urdu|اردو|246|Arab|1|South Asia
11|rus|Russian|Русский|210|Cyrl|0|Eurasia
12|deu|German|Deutsch|133|Latn|0|Europe
13|jpn|Japanese|日本語|126|Jpan|0|East Asia
14|pcm|Nigerian Pidgin|Naijá|121|Latn|0|West Africa
15|arz|Egyptian Arabic|مصرى|118|Arab|1|North Africa
16|mar|Marathi|मराठी|99|Deva|0|South Asia
17|tel|Telugu|తెలుగు|96|Telu|0|South Asia
18|tur|Turkish|Türkçe|90|Latn|0|West Asia
19|tam|Tamil|தமிழ்|87|Taml|0|South Asia
20|yue|Yue Chinese|粵語|86|Hant|0|East Asia
21|vie|Vietnamese|Tiếng Việt|86|Latn|0|Southeast Asia
22|wuu|Wu Chinese|吴语|83|Hans|0|East Asia
23|kor|Korean|한국어|82|Kore|0|East Asia
24|pnb|Western Punjabi|پنجابی|90|Arab|1|South Asia
25|jav|Javanese|Basa Jawa|84|Latn|0|Southeast Asia
26|ita|Italian|Italiano|68|Latn|0|Europe
27|hau|Hausa|Hausa|77|Latn|0|West Africa
28|tha|Thai|ไทย|61|Thai|0|Southeast Asia
29|guj|Gujarati|ગુજરાતી|62|Gujr|0|South Asia
30|pes|Iranian Persian|فارسی|77|Arab|1|West Asia
31|bho|Bhojpuri|भोजपुरी|53|Deva|0|South Asia
32|kan|Kannada|ಕನ್ನಡ|59|Knda|0|South Asia
33|apc|Levantine Arabic|الشامية|55|Arab|1|West Asia
34|swh|Swahili|Kiswahili|200|Latn|0|East Africa
35|pan|Eastern Punjabi|ਪੰਜਾਬੀ|52|Guru|0|South Asia
36|fil|Filipino|Filipino|83|Latn|0|Southeast Asia
37|pol|Polish|Polski|45|Latn|0|Europe
38|yor|Yoruba|Yorùbá|47|Latn|0|West Africa
39|ukr|Ukrainian|Українська|41|Cyrl|0|Europe
40|mal|Malayalam|മലയാളം|38|Mlym|0|South Asia
41|ory|Odia|ଓଡ଼ିଆ|38|Orya|0|South Asia
42|mya|Burmese|မြန်မာ|43|Mymr|0|Southeast Asia
43|pbu|Northern Pashto|پښتو|40|Arab|1|South Asia
44|snd|Sindhi|سنڌي|32|Arab|1|South Asia
45|amh|Amharic|አማርኛ|57|Ethi|0|East Africa
46|uzb|Uzbek|Oʻzbekcha|36|Latn|0|Central Asia
47|ron|Romanian|Română|25|Latn|0|Europe
48|azj|North Azerbaijani|Azərbaycan|24|Latn|0|West Asia
49|ceb|Cebuano|Cebuano|28|Latn|0|Southeast Asia
50|nld|Dutch|Nederlands|30|Latn|0|Europe
51|kmr|Kurmanji Kurdish|Kurmancî|20|Latn|0|West Asia
52|mag|Magahi|मगही|21|Deva|0|South Asia
53|npi|Nepali|नेपाली|32|Deva|0|South Asia
54|sin|Sinhala|සිංහල|17|Sinh|0|South Asia
55|khm|Khmer|ភាសាខ្មែរ|18|Khmr|0|Southeast Asia
56|mad|Madurese|Madhura|14|Latn|0|Southeast Asia
57|som|Somali|Soomaali|22|Latn|0|East Africa
58|aka|Akan|Akan|11|Latn|0|West Africa
59|ibo|Igbo|Igbo|31|Latn|0|West Africa
60|zsm|Standard Malay|Bahasa Melayu|80|Latn|0|Southeast Asia
61|hun|Hungarian|Magyar|13|Latn|0|Europe
62|ell|Greek|Ελληνικά|13|Grek|0|Europe
63|ces|Czech|Čeština|13|Latn|0|Europe
64|bel|Belarusian|Беларуская|5|Cyrl|0|Europe
65|kaz|Kazakh|Қазақша|16|Cyrl|0|Central Asia
66|tgk|Tajik|Тоҷикӣ|8|Cyrl|0|Central Asia
67|swe|Swedish|Svenska|13|Latn|0|Europe
68|heb|Hebrew|עברית|9|Hebr|1|West Asia
69|cat|Catalan|Català|9|Latn|0|Europe
70|bul|Bulgarian|Български|8|Cyrl|0|Europe
71|dan|Danish|Dansk|6|Latn|0|Europe
72|fin|Finnish|Suomi|5|Latn|0|Europe
73|slk|Slovak|Slovenčina|5|Latn|0|Europe
74|nob|Norwegian Bokmål|Norsk bokmål|5|Latn|0|Europe
75|hrv|Croatian|Hrvatski|7|Latn|0|Europe
76|srp|Serbian|Српски|12|Cyrl|0|Europe
77|bos|Bosnian|Bosanski|3|Latn|0|Europe
78|lit|Lithuanian|Lietuvių|3|Latn|0|Europe
79|lav|Latvian|Latviešu|2|Latn|0|Europe
80|ekk|Estonian|Eesti|1.1|Latn|0|Europe
81|slv|Slovenian|Slovenščina|2.5|Latn|0|Europe
82|als|Albanian Tosk|Shqip|6|Latn|0|Europe
83|hye|Armenian|Հայերեն|6|Armn|0|West Asia
84|kat|Georgian|ქართული|4|Geor|0|West Asia
85|khk|Halh Mongolian|Монгол|6|Cyrl|0|East Asia
86|lao|Lao|ລາວ|7|Laoo|0|Southeast Asia
87|hat|Haitian Creole|Kreyòl ayisyen|12|Latn|0|Caribbean
88|hil|Hiligaynon|Ilonggo|9|Latn|0|Southeast Asia
89|war|Waray|Winaray|3.6|Latn|0|Southeast Asia
90|min|Minangkabau|Baso Minang|6|Latn|0|Southeast Asia
91|sun|Sundanese|Basa Sunda|42|Latn|0|Southeast Asia
92|ban|Balinese|Basa Bali|3.3|Latn|0|Southeast Asia
93|bug|Buginese|Basa Ugi|4|Latn|0|Southeast Asia
94|wol|Wolof|Wolof|12|Latn|0|West Africa
95|twi|Twi|Twi|9|Latn|0|West Africa
96|ewe|Ewe|Eʋegbe|7|Latn|0|West Africa
97|mos|Mossi|Mòoré|8|Latn|0|West Africa
98|bam|Bambara|Bamanankan|14|Latn|0|West Africa
99|lin|Lingala|Lingála|20|Latn|0|Central Africa
100|lua|Luba-Kasai|Tshiluba|7|Latn|0|Central Africa
101|kik|Kikuyu|Gĩkũyũ|8|Latn|0|East Africa
102|luo|Dholuo|Dholuo|5|Latn|0|East Africa
103|nya|Nyanja|Chichewa|14|Latn|0|Southern Africa
104|sna|Shona|chiShona|11|Latn|0|Southern Africa
105|sot|Southern Sotho|Sesotho|6|Latn|0|Southern Africa
106|tsn|Tswana|Setswana|6|Latn|0|Southern Africa
107|tso|Tsonga|Xitsonga|4|Latn|0|Southern Africa
108|xho|Xhosa|isiXhosa|12|Latn|0|Southern Africa
109|zul|Zulu|isiZulu|14|Latn|0|Southern Africa
110|afr|Afrikaans|Afrikaans|17|Latn|0|Southern Africa
111|nso|Northern Sotho|Sesotho sa Leboa|5|Latn|0|Southern Africa
112|umb|Umbundu|Úmbúndú|6|Latn|0|Central Africa
113|bem|Bemba|IciBemba|4|Latn|0|Southern Africa
114|run|Rundi|Ikirundi|13|Latn|0|East Africa
115|kin|Kinyarwanda|Ikinyarwanda|15|Latn|0|East Africa
116|lug|Ganda|Luganda|11|Latn|0|East Africa
117|tir|Tigrinya|ትግርኛ|9|Ethi|0|East Africa
118|orm|Oromo|Afaan Oromoo|37|Latn|0|East Africa
119|arq|Algerian Arabic|الدارجة الجزائرية|36|Arab|1|North Africa
120|ary|Moroccan Arabic|الدارجة المغربية|33|Arab|1|North Africa
121|aeb|Tunisian Arabic|تونسي|12|Arab|1|North Africa
122|afb|Gulf Arabic|خليجي|9|Arab|1|West Asia
123|acw|Hijazi Arabic|حجازي|15|Arab|1|West Asia
124|ars|Najdi Arabic|نجدي|18|Arab|1|West Asia
125|apd|Sudanese Arabic|سودانية|32|Arab|1|North Africa
126|acm|Mesopotamian Arabic|عراقي|15|Arab|1|West Asia
127|tgl|Tagalog|Tagalog|45|Latn|0|Southeast Asia
128|ilo|Iloko|Ilokano|9|Latn|0|Southeast Asia
129|bcl|Central Bikol|Bikol|4|Latn|0|Southeast Asia
130|pam|Pampanga|Kapampangan|2.8|Latn|0|Southeast Asia
131|pag|Pangasinan|Pangasinan|1.5|Latn|0|Southeast Asia
132|ace|Acehnese|Bahsa Acèh|3.5|Latn|0|Southeast Asia
133|bjn|Banjar|Bahasa Banjar|4|Latn|0|Southeast Asia
134|bbc|Batak Toba|Hata Batak Toba|2|Latn|0|Southeast Asia
135|sas|Sasak|Sasak|2.1|Latn|0|Southeast Asia
136|mak|Makasar|Basa Mangkasara|2|Latn|0|Southeast Asia
137|tet|Tetum|Tetun|0.8|Latn|0|Southeast Asia
138|hsn|Xiang Chinese|湘语|38|Hans|0|East Asia
139|gan|Gan Chinese|赣语|22|Hans|0|East Asia
140|hak|Hakka Chinese|客家話|44|Hant|0|East Asia
141|nan|Min Nan Chinese|閩南語|50|Hant|0|East Asia
142|cjy|Jinyu Chinese|晋语|45|Hans|0|East Asia
143|cdo|Min Dong Chinese|閩東語|10|Hans|0|East Asia
144|asm|Assamese|অসমীয়া|15|Beng|0|South Asia
145|mai|Maithili|मैथिली|34|Deva|0|South Asia
146|awa|Awadhi|अवधी|4|Deva|0|South Asia
147|hne|Chhattisgarhi|छत्तीसगढ़ी|16|Deva|0|South Asia
148|bgc|Haryanvi|हरियाणवी|13|Deva|0|South Asia
149|mwr|Marwari|मारवाड़ी|8|Deva|0|South Asia
150|kas|Kashmiri|كٲشُر|7|Arab|1|South Asia
151|sat|Santali|ᱥᱟᱱᱛᱟᱲᱤ|7|Olck|0|South Asia
152|mni|Manipuri|মৈতৈলোন্|2|Beng|0|South Asia
153|doi|Dogri|डोगरी|2.6|Deva|0|South Asia
154|kok|Konkani|कोंकणी|2.5|Deva|0|South Asia
155|bod|Tibetan|བོད་སྐད|6|Tibt|0|East Asia
156|dzo|Dzongkha|རྫོང་ཁ|0.6|Tibt|0|South Asia
157|new|Newar|नेपाल भाषा|0.8|Deva|0|South Asia
158|brx|Bodo|बर'|1.5|Deva|0|South Asia
159|lus|Mizo|Mizo ṭawng|1|Latn|0|South Asia
160|kha|Khasi|Khasi|1.2|Latn|0|South Asia
161|shn|Shan|လိၵ်ႈတႆး|3.3|Mymr|0|Southeast Asia
162|ksw|S'gaw Karen|ကညီကျိာ်|2|Mymr|0|Southeast Asia
163|tts|Northeastern Thai|ภาษาอีสาน|20|Thai|0|Southeast Asia
164|nod|Northern Thai|ᨣᩴᩤᨾᩮᩬᩥᨦ|6|Lana|0|Southeast Asia
165|ckb|Central Kurdish|سۆرانی|8|Arab|1|West Asia
166|prs|Dari|دری|19|Arab|1|South Asia
167|pbt|Southern Pashto|پښتو|20|Arab|1|South Asia
168|bal|Balochi|بلوچی|8|Arab|1|South Asia
169|tuk|Turkmen|Türkmençe|7|Latn|0|Central Asia
170|kir|Kyrgyz|Кыргызча|5|Cyrl|0|Central Asia
171|tat|Tatar|Татарча|5|Cyrl|0|Eurasia
172|bak|Bashkir|Башҡортса|1.4|Cyrl|0|Eurasia
173|chv|Chuvash|Чӑвашла|1|Cyrl|0|Eurasia
174|sah|Yakut|Саха тыла|0.5|Cyrl|0|North Asia
175|udm|Udmurt|Удмурт|0.3|Cyrl|0|Eurasia
176|che|Chechen|Нохчийн|1.5|Cyrl|0|West Asia
177|ava|Avar|Авар мацӏ|0.8|Cyrl|0|West Asia
178|lez|Lezgi|Лезги|0.6|Cyrl|0|West Asia
179|oss|Ossetic|Ирон|0.6|Cyrl|0|West Asia
180|azb|South Azerbaijani|تۆرکجه|16|Arab|1|West Asia
181|glk|Gilaki|گیلکی|2.5|Arab|1|West Asia
182|mzn|Mazanderani|مازِرونی|2|Arab|1|West Asia
183|lrc|Northern Luri|لۊری|1.5|Arab|1|West Asia
184|lki|Laki|لەکی|1|Arab|1|West Asia
185|sdh|Southern Kurdish|کوردی خوارین|3|Arab|1|West Asia
186|ayl|Libyan Arabic|ليبي|4|Arab|1|North Africa
187|kab|Kabyle|Taqbaylit|6|Latn|0|North Africa
188|tzm|Central Atlas Tamazight|ⵜⴰⵎⴰⵣⵉⵖⵜ|3|Tfng|0|North Africa
189|rif|Tarifit|Tmaziɣt|1.5|Latn|0|North Africa
190|shy|Shawiya|Tacawit|2|Latn|0|North Africa
191|mlt|Maltese|Malti|0.5|Latn|0|Europe
192|isl|Icelandic|Íslenska|0.4|Latn|0|Europe
193|fao|Faroese|Føroyskt|0.07|Latn|0|Europe
194|gle|Irish|Gaeilge|1.9|Latn|0|Europe
195|gla|Scottish Gaelic|Gàidhlig|0.09|Latn|0|Europe
196|cym|Welsh|Cymraeg|0.7|Latn|0|Europe
197|bre|Breton|Brezhoneg|0.2|Latn|0|Europe
198|glg|Galician|Galego|2.4|Latn|0|Europe
199|eus|Basque|Euskara|0.9|Latn|0|Europe
200|ast|Asturian|Asturianu|0.1|Latn|0|Europe
201|oci|Occitan|Occitan|0.5|Latn|0|Europe
202|lld|Ladin|Ladin|0.04|Latn|0|Europe
203|fur|Friulian|Furlan|0.4|Latn|0|Europe
204|vec|Venetian|Vèneto|4|Latn|0|Europe
205|nap|Neapolitan|Napulitano|5.7|Latn|0|Europe
206|scn|Sicilian|Sicilianu|4.7|Latn|0|Europe
207|srd|Sardinian|Sardu|1|Latn|0|Europe
208|rmy|Vlax Romani|Romani|1.5|Latn|0|Europe
209|mkd|Macedonian|Македонски|2|Cyrl|0|Europe
210|cnr|Montenegrin|Crnogorski|0.2|Latn|0|Europe
211|que|Quechua|Runasimi|9|Latn|0|South America
212|ayr|Central Aymara|Aymar aru|1.7|Latn|0|South America
213|gug|Paraguayan Guarani|Avañe'ẽ|6|Latn|0|South America
214|nhe|Eastern Huasteca Nahuatl|Nahuatl|1.7|Latn|0|Mesoamerica
215|yua|Yucatec Maya|Maaya t'aan|0.8|Latn|0|Mesoamerica
216|quc|K'iche'|Qatzijob'al|1.1|Latn|0|Mesoamerica
217|kek|Q'eqchi'|Q'eqchi'|1.1|Latn|0|Mesoamerica
218|mam|Mam|Qyol Mam|0.6|Latn|0|Mesoamerica
219|cak|Kaqchikel|Kaqchikel|0.5|Latn|0|Mesoamerica
220|jam|Jamaican Creole|Jamiekan|3.2|Latn|0|Caribbean
221|gcf|Guadeloupean Creole|Kréyòl Gwadloup|0.4|Latn|0|Caribbean
222|pap|Papiamento|Papiamentu|0.3|Latn|0|Caribbean
223|srn|Sranan Tongo|Sranantongo|0.5|Latn|0|South America
224|tpi|Tok Pisin|Tok Pisin|4|Latn|0|Oceania
225|pis|Pijin|Pijin|0.3|Latn|0|Oceania
226|bis|Bislama|Bislama|0.2|Latn|0|Oceania
227|fij|Fijian|Na Vosa Vakaviti|0.4|Latn|0|Oceania
228|smo|Samoan|Gagana Samoa|0.5|Latn|0|Oceania
229|ton|Tongan|Lea faka-Tonga|0.2|Latn|0|Oceania
230|mri|Maori|Te Reo Māori|0.2|Latn|0|Oceania
231|haw|Hawaiian|ʻŌlelo Hawaiʻi|0.02|Latn|0|Oceania
232|cha|Chamorro|Fino' Chamoru|0.06|Latn|0|Oceania
233|mah|Marshallese|Kajin M̧ajeļ|0.05|Latn|0|Oceania
234|pon|Pohnpeian|Lokaiahn Pohnpei|0.03|Latn|0|Oceania
235|chk|Chuukese|Chuuk|0.05|Latn|0|Oceania
236|grc|Ancient Greek|Ἑλληνική|0.01|Grek|0|Historical
237|hbo|Ancient Hebrew|עברית מקראית|0.01|Hebr|1|Historical
238|lat|Latin|Latina|0.05|Latn|0|Historical
239|chu|Church Slavonic|Цркъвьнословѣньскъ|0.05|Cyrl|0|Historical
240|cop|Coptic|Ⲙⲉⲧⲣⲉⲙ̀ⲛⲭⲏⲙⲓ|0.01|Copt|0|Historical
241|syc|Classical Syriac|ܣܘܪܝܝܐ|0.05|Syrc|1|West Asia
242|aii|Assyrian Neo-Aramaic|ܣܘܪܝܬ|0.2|Syrc|1|West Asia
243|amw|Western Neo-Aramaic|ܐܪܡܝܬ|0.02|Syrc|1|West Asia
244|fuv|Nigerian Fulfulde|Fulfulde|16|Latn|0|West Africa
245|ffm|Maasina Fulfulde|Fulfulde|1|Latn|0|West Africa
246|fub|Adamawa Fulfulde|Fulfulde|5|Latn|0|West Africa
247|dyu|Dyula|Julakan|12|Latn|0|West Africa
248|sus|Susu|Sosoxui|1.2|Latn|0|West Africa
249|men|Mende|Mɛnde yia|2|Latn|0|West Africa
250|tem|Timne|KʌThemnɛ|1.4|Latn|0|West Africa
251|kpe|Kpelle|Kpɛlɛɛ|1.3|Latn|0|West Africa
252|vai|Vai|ꕙꔤ|0.1|Vaii|0|West Africa
253|dav|Taita|Kidawida|0.4|Latn|0|East Africa
254|kam|Kamba|Kikamba|4|Latn|0|East Africa
255|mer|Meru|Kĩmĩĩrũ|2|Latn|0|East Africa
256|guz|Gusii|Ekegusii|2.2|Latn|0|East Africa
257|luy|Luyia|Luluhya|5|Latn|0|East Africa
258|swc|Congo Swahili|Kiswahili ya Kongo|9|Latn|0|Central Africa
259|kon|Kongo|Kikongo|7|Latn|0|Central Africa
260|loz|Lozi|Silozi|0.7|Latn|0|Southern Africa
261|toi|Tonga Zambia|Chitonga|1.5|Latn|0|Southern Africa
262|tum|Tumbuka|chiTumbuka|2.5|Latn|0|Southern Africa
263|ven|Venda|Tshivenḓa|1.3|Latn|0|Southern Africa
264|nbl|Southern Ndebele|isiNdebele|1.1|Latn|0|Southern Africa
265|ndc|Ndau|chiNdau|2.4|Latn|0|Southern Africa
266|kmb|Kimbundu|Kimbundu|4|Latn|0|Central Africa
267|kqn|Kaonde|Kikaonde|0.2|Latn|0|Southern Africa
268|lun|Lunda|Chilunda|0.4|Latn|0|Southern Africa
269|her|Herero|Otjiherero|0.2|Latn|0|Southern Africa
270|kua|Kwanyama|Oshikwanyama|0.4|Latn|0|Southern Africa
271|ndo|Ndonga|Oshindonga|0.8|Latn|0|Southern Africa
272|sag|Sango|Sängö|5|Latn|0|Central Africa
273|zar|Zarma|Zarmaciine|4|Latn|0|West Africa
274|knc|Central Kanuri|Kanuri|4|Latn|0|West Africa
275|shu|Chadian Arabic|شوا|1.6|Arab|1|Central Africa
276|sad|Sandawe|Sandaweeki|0.06|Latn|0|East Africa
277|had|Hadza|Hadzane|0.001|Latn|0|East Africa
278|sid|Sidamo|Sidaamu Afoo|3|Latn|0|East Africa
279|wal|Wolaytta|Wolayttatto doonaa|2|Latn|0|East Africa
280|aar|Afar|Qafaraf|2|Latn|0|East Africa
281|bej|Beja|Bidhaawyeet|2|Arab|1|East Africa
282|nus|Nuer|Thok Naath|1.7|Latn|0|East Africa
283|din|Dinka|Thuɔŋjäŋ|4|Latn|0|East Africa
284|ach|Acoli|Lwo|1.5|Latn|0|East Africa
285|lgg|Lugbara|Lugbarati|1.7|Latn|0|East Africa
286|teo|Teso|Ateso|1.9|Latn|0|East Africa
287|nyn|Nyankole|Runyankore|3.4|Latn|0|East Africa
288|cgg|Chiga|Rukiga|2.3|Latn|0|East Africa
289|sog|Soga|Lusoga|3|Latn|0|East Africa
290|nyo|Nyoro|Runyoro|1|Latn|0|East Africa
291|kdj|Karamojong|ŋaKaramojong|0.7|Latn|0|East Africa
292|mas|Masai|ɔl Maa|1.5|Latn|0|East Africa
293|saq|Samburu|Sampur|0.2|Latn|0|East Africa
294|tuv|Turkana|Ng'aturkana|1.2|Latn|0|East Africa
295|naq|Nama|Khoekhoegowab|0.3|Latn|0|Southern Africa
296|hif|Fiji Hindi|Fiji Baat|0.4|Latn|0|Oceania
297|pih|Pitcairn-Norfolk|Norfuk|0.001|Latn|0|Oceania
298|crs|Seselwa Creole French|Seselwa|0.1|Latn|0|East Africa
299|mfe|Morisyen|Morisien|1.1|Latn|0|East Africa
300|epo|Esperanto|Esperanto|2|Latn|0|Worldwide
"""

ALIASES = {
    "arb": ["ara", "arb", "ar"],
    "cmn": ["cmn", "zho", "chi", "zh"],
    "ind": ["ind", "msa", "zlm"],
    "zsm": ["zsm", "msa", "zlm", "may"],
    "pes": ["pes", "fas", "per", "fa"],
    "prs": ["prs", "fas", "pes"],
    "pbu": ["pbu", "pus", "pbt", "pst"],
    "pbt": ["pbt", "pus", "pbu"],
    "npi": ["npi", "nep"],
    "ory": ["ory", "ori"],
    "swh": ["swh", "swa", "sw"],
    "swc": ["swc", "swa", "swh"],
    "fil": ["fil", "tgl", "tl"],
    "tgl": ["tgl", "fil", "tl"],
    "als": ["als", "sqi", "sq"],
    "ekk": ["ekk", "est", "et"],
    "nob": ["nob", "nor", "nb", "no"],
    "khk": ["khk", "mon", "mn"],
    "azj": ["azj", "aze", "az"],
    "azb": ["azb", "aze"],
    "ckb": ["ckb", "kur", "ku"],
    "kmr": ["kmr", "kur", "ku"],
    "que": ["que", "quz", "qxc", "qu"],
    "gug": ["gug", "grn", "gn"],
    "ayr": ["ayr", "aym", "ay"],
    "fuv": ["fuv", "ful", "ff"],
    "fub": ["fub", "ful", "ff"],
    "ffm": ["ffm", "ful", "ff"],
    "aka": ["aka", "twi", "fat", "ak"],
    "twi": ["twi", "aka", "ak"],
    "kon": ["kon", "kng", "kg"],
    "lua": ["lua", "lub"],
    "hye": ["hye", "arm", "hy"],
    "ell": ["ell", "gre", "el"],
    "grc": ["grc", "ell"],
    "heb": ["heb", "he"],
    "hbo": ["hbo", "heb"],
    "mya": ["mya", "bur", "my"],
    "kat": ["kat", "geo", "ka"],
    "eus": ["eus", "baq", "eu"],
    "cym": ["cym", "wel", "cy"],
    "gle": ["gle", "gle", "ga"],
    "gla": ["gla", "gd"],
    "mri": ["mri", "mao", "mi"],
    "lat": ["lat", "la"],
    "epo": ["epo", "eo"],
    "srp": ["srp", "sr"],
    "hrv": ["hrv", "hr"],
    "bos": ["bos", "bs"],
    "mkd": ["mkd", "mac", "mk"],
    "slk": ["slk", "slo", "sk"],
    "slv": ["slv", "sl"],
    "ron": ["ron", "rum", "ro"],
    "ces": ["ces", "cze", "cs"],
    "nld": ["nld", "dut", "nl"],
    "deu": ["deu", "ger", "de"],
    "fra": ["fra", "fre", "fr"],
    "spa": ["spa", "es"],
    "por": ["por", "pt"],
    "ita": ["ita", "it"],
    "rus": ["rus", "ru"],
    "ukr": ["ukr", "uk"],
    "pol": ["pol", "pl"],
    "tur": ["tur", "tr"],
    "vie": ["vie", "vi"],
    "tha": ["tha", "th"],
    "kor": ["kor", "ko"],
    "jpn": ["jpn", "ja"],
    "hin": ["hin", "hi"],
    "ben": ["ben", "bn"],
    "urd": ["urd", "ur"],
    "tam": ["tam", "ta"],
    "tel": ["tel", "te"],
    "kan": ["kan", "kn"],
    "mal": ["mal", "ml"],
    "guj": ["guj", "gu"],
    "pan": ["pan", "pa"],
    "yue": ["yue", "zh"],
    "wuu": ["wuu", "zh"],
    "nan": ["nan", "zh"],
    "hak": ["hak", "zh"],
    "ilo": ["ilo", "il"],
    "ceb": ["ceb"],
    "hat": ["hat", "ht"],
    "afr": ["afr", "af"],
    "amh": ["amh", "am"],
    "som": ["som", "so"],
    "ibo": ["ibo", "ig"],
    "yor": ["yor", "yo"],
    "hau": ["hau", "ha"],
    "uzb": ["uzb", "uz"],
    "kaz": ["kaz", "kk"],
    "kir": ["kir", "ky"],
    "tuk": ["tuk", "tk"],
    "tgk": ["tgk", "tg"],
    "bel": ["bel", "be"],
    "bul": ["bul", "bg"],
    "hun": ["hun", "hu"],
    "fin": ["fin", "fi"],
    "swe": ["swe", "sv"],
    "dan": ["dan", "da"],
    "lit": ["lit", "lt"],
    "lav": ["lav", "lv"],
    "cat": ["cat", "ca"],
    "glg": ["glg", "gl"],
    "oci": ["oci", "oc"],
    "bre": ["bre", "br"],
    "mlt": ["mlt", "mt"],
    "isl": ["isl", "is"],
    "fao": ["fao", "fo"],
    "lao": ["lao", "lo"],
    "khm": ["khm", "km"],
    "sin": ["sin", "si"],
    "nep": ["npi", "ne"],
    "bod": ["bod", "bo"],
    "dzo": ["dzo", "dz"],
    "mon": ["khk", "mn"],
    "fas": ["pes", "fa"],
    "pus": ["pbu", "ps"],
    "kur": ["kmr", "ku"],
    "tir": ["tir", "ti"],
    "orm": ["orm", "om"],
    "sna": ["sna", "sn"],
    "nya": ["nya", "ny"],
    "xho": ["xho", "xh"],
    "zul": ["zul", "zu"],
    "sot": ["sot", "st"],
    "tsn": ["tsn", "tn"],
    "tso": ["tso", "ts"],
    "ven": ["ven", "ve"],
    "nso": ["nso"],
    "lin": ["lin", "ln"],
    "sag": ["sag", "sg"],
    "kin": ["kin", "rw"],
    "run": ["run", "rn"],
    "lug": ["lug", "lg"],
    "wol": ["wol", "wo"],
    "ewe": ["ewe", "ee"],
    "bam": ["bam", "bm"],
    "mos": ["mos"],
    "pcm": ["pcm"],
    "tpi": ["tpi"],
    "smo": ["smo", "sm"],
    "ton": ["ton", "to"],
    "fij": ["fij", "fj"],
    "mah": ["mah", "mh"],
    "cha": ["cha", "ch"],
    "haw": ["haw"],
    "pap": ["pap"],
    "jam": ["jam"],
    "crs": ["crs"],
    "mfe": ["mfe"],
    "chk": ["chk"],
    "pon": ["pon"],
    "cop": ["cop"],
    "chu": ["chu", "cu"],
    "syc": ["syc", "syr"],
    "aii": ["aii", "syr"],
}


def parse_seed():
    rows = []
    seen = set()
    for line in SEED.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        rank, iso, name, native, speakers, script, rtl, region = line.split("|")
        if iso in seen:
            continue
        seen.add(iso)
        rows.append(
            {
                "rank": int(rank),
                "iso": iso,
                "name": name,
                "native": native,
                "speakersM": float(speakers),
                "script": script,
                "rtl": rtl == "1",
                "region": region,
            }
        )
    return rows
