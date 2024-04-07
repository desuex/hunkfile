from HunkfileCodec import HunkfileCodec


def main():
    codec = HunkfileCodec("../assets/hnk/", "../assets/xls/")
    codec.dump_global_en("Global_en_US.hnk")
    codec.dump_loca("Localisation_en_US.hnk")

if __name__ == "__main__":
    main()
