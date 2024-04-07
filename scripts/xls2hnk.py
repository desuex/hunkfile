from HunkfileCodec import HunkfileCodec


def main():
    raise NotImplementedError("This function has not been implemented yet.")
    codec = HunkfileCodec("../assets/hnk/", "../assets/xls/")
    # dataGlobal = codec.parse("Global_en_US.hnk")
    dataLocal = codec.parse("Localisation_en_US.hnk")
    dialog = codec.import_excel("Dialog.xls", 0)  # dialog
    common = codec.import_excel("Common.xls", 0)  # common
    lc_pc = codec.import_excel("lcPc.xls", 0)  # lcPC
    lc_common = codec.import_excel("lcCommon.xls", 0)  # lcCommon
    dataLocal[2] = common
    dataLocal[6] = dialog
    dataLocal[10] = lc_common
    dataLocal[14] = lc_pc
    #
    codec.pack(dataLocal, "Localisation_en_US.hnk")


if __name__ == "__main__":
    main()