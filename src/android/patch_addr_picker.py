import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) 字段：地址改成三级下拉 + 街道
s = s.replace(
    "    private EditText etStoreName, etCollector, etArea, etAddress;",
    "    private EditText etStoreName, etCollector, etArea, etStreet;\n"
    "    private android.widget.Spinner spProv, spCity, spDist;\n"
    "    private String[] provArr = new String[0];\n"
    "    private String[][] cityArr = new String[0][];\n"
    "    private String[][][] distArr = new String[0][][];")

# 2) UI：替换地址输入块
old_ui = '''        TextView lAddr = new TextView(this);
        lAddr.setText("现场地址（必填：省市 + 街道门牌号）");
        lAddr.setTextSize(16);
        lAddr.setTextColor(MUTED);
        lAddr.setPadding(dp(4), dp(20), 0, dp(8));
        content.addView(lAddr);

        etAddress = new EditText(this);
        etAddress.setHint("例如：广东省湛江市赤坎区人民大道 88 号");
        etAddress.setTextSize(18);
        etAddress.setTextColor(TEXT);
        etAddress.setHintTextColor(Color.parseColor("#A8B4C6"));
        etAddress.setBackground(roundRect(CARD, 12));
        etAddress.setPadding(dp(16), dp(12), dp(16), dp(12));
        etAddress.setMinLines(2);
        etAddress.setText(site.address == null ? "" : site.address);
        content.addView(etAddress, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(76)));'''

new_ui = '''        TextView lAddr = new TextView(this);
        lAddr.setText("现场地址（必填：先选省市区，再填街道门牌号）");
        lAddr.setTextSize(16);
        lAddr.setTextColor(MUTED);
        lAddr.setPadding(dp(4), dp(20), 0, dp(8));
        content.addView(lAddr);

        LinearLayout addrRow = new LinearLayout(this);
        addrRow.setOrientation(LinearLayout.HORIZONTAL);
        content.addView(addrRow, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(54)));

        spProv = new android.widget.Spinner(this);
        spProv.setBackground(roundRect(CARD, 12));
        spProv.setAdapter(new android.widget.ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item, new String[]{"省份"}));
        addrRow.addView(spProv, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1f));

        spCity = new android.widget.Spinner(this);
        spCity.setBackground(roundRect(CARD, 12));
        spCity.setAdapter(new android.widget.ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item, new String[]{"城市"}));
        LinearLayout.LayoutParams clp2 = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1f);
        clp2.leftMargin = dp(8);
        addrRow.addView(spCity, clp2);

        spDist = new android.widget.Spinner(this);
        spDist.setBackground(roundRect(CARD, 12));
        spDist.setAdapter(new android.widget.ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item, new String[]{"区 / 县"}));
        LinearLayout.LayoutParams dlp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1f);
        dlp.leftMargin = dp(8);
        addrRow.addView(spDist, dlp);

        etStreet = new EditText(this);
        etStreet.setHint("街道、门牌号、园区或楼栋");
        etStreet.setTextSize(18);
        etStreet.setTextColor(TEXT);
        etStreet.setHintTextColor(Color.parseColor("#A8B4C6"));
        etStreet.setBackground(roundRect(CARD, 12));
        etStreet.setPadding(dp(16), dp(12), dp(16), dp(12));
        LinearLayout.LayoutParams slp2 = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(58));
        slp2.topMargin = dp(8);
        content.addView(etStreet, slp2);

        spProv.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(android.widget.AdapterView<?> p, View v, int pos, long id) {
                updateCities(pos);
            }
            @Override public void onNothingSelected(android.widget.AdapterView<?> p) { }
        });
        spCity.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(android.widget.AdapterView<?> p, View v, int pos, long id) {
                updateDistricts(pos);
            }
            @Override public void onNothingSelected(android.widget.AdapterView<?> p) { }
        });'''

assert old_ui in s
s = s.replace(old_ui, new_ui)

# 3) 校验并拼地址
old_val = '''        String addr = etAddress.getText().toString().trim();
        if (addr.isEmpty()) {
            toast("请先填写现场地址");
            etAddress.requestFocus();
            return;
        }'''
new_val = '''        int pi = spProv.getSelectedItemPosition();
        int ci = spCity.getSelectedItemPosition();
        int di = spDist.getSelectedItemPosition();
        if (pi <= 0 || ci < 0 || di < 0) {
            toast("请先选择省 / 市 / 区");
            return;
        }
        String street = etStreet.getText().toString().trim();
        if (street.isEmpty()) {
            toast("请填写街道门牌号");
            etStreet.requestFocus();
            return;
        }
        String provName = provArr[pi];
        String cityName = cityArr[pi - 1][ci];
        String distName = distArr[pi - 1][ci][di];
        String addr = provName + ("市辖区".equals(cityName) ? "" : cityName) + distName + street;'''

assert old_val in s
s = s.replace(old_val, new_val)

# 4) 地区数据加载 + 级联方法（插到 confirmRestart 之前）
anchor = '    private void confirmRestart() {'
methods = '''    /** 从 res/raw/pca.json 读省市区（31 省 / 300+ 市 / 2900+ 区县） */
    private void loadRegions() {
        if (provArr.length > 0) return;
        new Thread(() -> {
            try {
                java.io.InputStream in = getResources().openRawResource(R.raw.pca);
                java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
                byte[] buf = new byte[8192];
                int n;
                while ((n = in.read(buf)) > 0) bos.write(buf, 0, n);
                in.close();
                org.json.JSONArray arr = new org.json.JSONArray(bos.toString("UTF-8"));
                String[] provs = new String[arr.length() + 1];
                String[][] cities = new String[arr.length()][];
                String[][][] dists = new String[arr.length()][][];
                provs[0] = "省份";
                for (int i = 0; i < arr.length(); i++) {
                    org.json.JSONObject po = arr.getJSONObject(i);
                    provs[i + 1] = po.getString("name");
                    org.json.JSONArray cs = po.optJSONArray("children");
                    int cn = cs == null ? 0 : cs.length();
                    cities[i] = new String[cn];
                    dists[i] = new String[cn][];
                    for (int j = 0; j < cn; j++) {
                        org.json.JSONObject co = cs.getJSONObject(j);
                        cities[i][j] = co.getString("name");
                        org.json.JSONArray ds = co.optJSONArray("children");
                        int dn = ds == null ? 0 : ds.length();
                        dists[i][j] = new String[dn];
                        for (int k = 0; k < dn; k++) dists[i][j][k] = ds.getJSONObject(k).getString("name");
                    }
                }
                runOnUiThread(() -> {
                    provArr = provs;
                    cityArr = cities;
                    distArr = dists;
                    spProv.setAdapter(new android.widget.ArrayAdapter<String>(MainActivity.this,
                            android.R.layout.simple_spinner_dropdown_item, provArr));
                });
            } catch (Exception e) {
                runOnUiThread(() -> toast("地址数据加载失败：" + e.getMessage()));
            }
        }).start();
    }

    private void updateCities(int provPos) {
        if (provPos <= 0 || provPos - 1 >= cityArr.length) {
            spCity.setAdapter(new android.widget.ArrayAdapter<String>(this,
                    android.R.layout.simple_spinner_dropdown_item, new String[]{"城市"}));
            return;
        }
        String[] cs = cityArr[provPos - 1];
        spCity.setAdapter(new android.widget.ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item, cs.length == 0 ? new String[]{"城市"} : cs));
        updateDistricts(0);
    }

    private void updateDistricts(int cityPos) {
        int provPos = spProv.getSelectedItemPosition();
        if (provPos <= 0 || provPos - 1 >= distArr.length) return;
        String[][] ds = distArr[provPos - 1];
        if (cityPos < 0 || cityPos >= ds.length) {
            spDist.setAdapter(new android.widget.ArrayAdapter<String>(this,
                    android.R.layout.simple_spinner_dropdown_item, new String[]{"区 / 县"}));
            return;
        }
        spDist.setAdapter(new android.widget.ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item, ds[cityPos]));
    }

'''
assert anchor in s
s = s.replace(anchor, methods + anchor)

# 5) onCreate 里加载地区数据
s = s.replace('        loadScenes();          // 公开接口，不需要登录就能拉',
              '        loadScenes();          // 公开接口，不需要登录就能拉\n        loadRegions();         // 省市区数据（本地资源）')

io.open(p, 'w', encoding='utf-8').write(s)
print('address 3-level patched')
