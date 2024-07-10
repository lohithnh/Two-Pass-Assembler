import streamlit as st

def display_file_contents(filename):
    # st.subheader(f"Contents of {filename}:")
    with open(filename, "r") as file:
        for line in file:
            st.text(line.strip())

def convert_files(intermed_file, symtab_file):
    mnemonic = ["LDA", "STA", "LDCH", "STCH"]
    code = ["33", "44", "53", "57"]

    with open(intermed_file.name, "r") as fp3, open(symtab_file.name, "r") as fp2, open("ASSMLIST.DAT", "w") as fp1, open("OBJCODE.DAT", "w") as fp4:
        label, opcode, operand = fp3.readline().split()

        address = None
        prevaddr = None
        while opcode != "END":
            prevaddr = address
            address, label, opcode, operand = map(str.strip, fp3.readline().split())

        finaddr = int(address)
        fp3.seek(0)
        label, opcode, operand = fp3.readline().split()

        if opcode == "START":
            fp1.write(f"\t{label}\t{opcode}\t{operand}\n")
            fp4.write(f"H^{label}^00{operand}^00{finaddr}\n")
            address, label, opcode, operand = map(str.strip, fp3.readline().split())
            st = int(address)
            prevaddr = int(prevaddr) if prevaddr else 0
            diff = prevaddr - st
            fp4.write(f"T^00{address}^{diff}\n")

        j = 0
        while opcode != "END":
            if opcode == "BYTE":
                fp1.write(f"{address}\t{label}\t{opcode}\t{operand}\t")
                actual_len = len(operand) - 3
                fp4.write("^")
                for i in range(2, actual_len + 2):
                    ad = hex(ord(operand[i]))[2:].upper()
                    fp1.write(ad)
                    fp4.write(ad)
                fp1.write("\n")

            elif opcode == "WORD":
                fp1.write(f"{address}\t{label}\t{opcode}\t{operand}\t00000{operand}\n")
                fp4.write(f"^00000{operand}")

            elif opcode in ["RESB", "RESW"]:
                fp1.write(f"{address}\t{label}\t{opcode}\t{operand}\n")

            else:
                while opcode != mnemonic[j]:
                    j += 1
                if operand == "COPY":
                    fp1.write(f"{address}\t{label}\t{opcode}\t{operand}\t{code[j]}0000\n")
                else:
                    fp2.seek(0)
                    for line in fp2:
                        symbol, add = map(str.strip, line.split())
                        if operand == symbol:
                            break
                    fp1.write(f"{address}\t{label}\t{opcode}\t{operand}\t{code[j]}{add}\n")
                    fp4.write(f"^{code[j]}{add}")

            address, label, opcode, operand = map(str.strip, fp3.readline().split())

        fp1.write(f"{address}\t{label}\t{opcode}\t{operand}\n")
        fp4.write(f"\nE^00{st}")

    print("\nIntermediate file is converted into object code")

st.title("File Contents Viewer and Converter")
st.sidebar.title("Upload Files")

intermed_file = st.sidebar.file_uploader("Upload INTERMED.DAT", type=["dat"])
symtab_file = st.sidebar.file_uploader("Upload SYMTAB.DAT", type=["dat"])

if intermed_file and symtab_file:
    convert_button = st.sidebar.button("Convert Files")
    if convert_button:
        st.subheader("Contents of INTERMED.DAT:")
        display_file_contents(intermed_file.name)
        st.subheader("Contents of SYMTAB.DAT:")
        display_file_contents(symtab_file.name)
        convert_files(intermed_file, symtab_file)
        st.subheader("Contents of ASSMLIST.DAT:")
        display_file_contents("ASSMLIST.DAT")
        st.subheader("Contents of OBJCODE.DAT:")
        display_file_contents("OBJCODE.DAT")
