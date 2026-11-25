def halo (nama):
    return nama

def hitung_diskon(harga, persen_diskon):
    if harga < 0 or persen_diskon < 0 or persen_diskon > 100:
        return 0.0
    potongan = harga * (persen_diskon / 100)
    harga_akhir = harga - potongan
    if harga_akhir >= 100000:
        harga_akhir -= 5000
    return round(harga_akhir, 2)