from fastapi import APIRouter, HTTPException
import os
import subprocess
from API.utils import pj_path, errorHandling, split_list


router = APIRouter(
    tags=["processes"],
    responses={404: {"description": "Not found"}},
)


@router.put("/preprocess", summary="最新のMPCデータを取得", tags=["processes"], status_code=200)
def run_preprocess(pj: int = -1):

    os.chdir(pj_path(pj).as_posix())
    result = subprocess.run(["preprocess"])
    errorHandling(result.returncode)


@router.put("/startsearch2R", summary="ビニング&マスク", tags=["processes"], status_code=200)
def run_startsearch2R(binning: int = 2, pj: int = -1, sn: int = 2000):

    if binning != 2 and binning != 4:
        raise HTTPException(status_code=400)
    else:
        binning = str(binning)

    os.chdir(pj_path(pj).as_posix())
    result = subprocess.run(
        ["startsearch2R", "sn={}".format(sn)], input=binning, encoding="UTF-8"
    )
    errorHandling(result.returncode)


@router.put(
    "/prempsearchC-before",
    summary="精密軌道取得(確定番号付き天体)",
    tags=["processes"],
    status_code=200,
)
def run_prempsearchC_before(pj: int = -1):

    os.chdir(pj_path(pj).as_posix())
    result = subprocess.run(["prempsearchC-before"], shell=True)
    errorHandling(result.returncode)


@router.put(
    "/prempsearchC-after", summary="精密軌道取得(仮符号天体)", tags=["processes"], status_code=200
)
def run_prempsearchC_after(pj: int = -1):

    os.chdir(pj_path(pj).as_posix())
    result = subprocess.run(["prempsearchC-after"], shell=True)
    errorHandling(result.returncode)


@router.put("/astsearch_new", summary="自動検出", tags=["processes"], status_code=200)
def run_astsearch_new(pj: int = -1, nd: int = 4, ar: int = 6):

    os.chdir(pj_path(pj).as_posix())
    cmdStr = "astsearch_new nd={} ar={}".format(nd, ar)
    print(cmdStr)
    result = subprocess.run(cmdStr, shell=True)
    errorHandling(result.returncode)


@router.put(
    "/getMPCORB_and_mpc2edb",
    summary="小惑星の軌道情報をMPCから取得",
    tags=["processes"],
    status_code=200,
)
def run_getMPCORB_and_mpc2edb(pj: int = -1):

    os.chdir(pj_path(pj).as_posix())
    result = subprocess.run(["getMPCORB_and_mpc2edb_for_button"])
    errorHandling(result.returncode)


@router.put(
    "/AstsearchR_between_COIAS_and_ReCOIAS",
    summary="探索モード後に走り自動検出天体の番号の付け替えを行う",
    tags=["processes"],
)
def run_AstsearchR_between_COIAS_and_ReCOIAS(num: int, pj: int = -1):

    os.chdir(pj_path(pj).as_posix())
    resultError = subprocess.run(["AstsearchR_between_COIAS_and_ReCOIAS", str(num)])
    errorHandling(resultError.returncode)
    redisp_path = pj_path(pj) / "redisp.txt"

    if not redisp_path.is_file():
        raise HTTPException(status_code=404)

    with redisp_path.open() as f:
        result = f.read()

    result = split_list(result.split(), 4)

    return result


@router.put(
    "/AstsearchR_afterReCOIAS", summary="レポートモードに入ったとき発火し、send_mpcを作成", tags=["processes"]
)
def run_Astsearch_afterReCOIAS(pj: int = -1):

    os.chdir(pj_path(pj).as_posix())
    resultError = subprocess.run(["AstsearchR_afterReCOIAS"])
    errorHandling(resultError.returncode)

    send_path = pj_path(pj) / "send_mpc.txt"
    result = ""

    with send_path.open(mode="r") as f:
        result = f.read()

    if not send_path.is_file():
        raise HTTPException(status_code=404)

    return {"send_mpc": result}


@router.put("/AstsearchR_after_manual", summary="手動測定：再描画による確認作業", tags=["processes"])
def run_AstsearchR_after_manual(pj: int = -1):

    os.chdir(pj_path(pj).as_posix())
    resultError = subprocess.run(["AstsearchR_after_manual"])
    errorHandling(resultError.returncode)

    send_path = pj_path(pj) / "reredisp.txt"
    result = ""

    with send_path.open(mode="r") as f:
        result = f.read()

    if not send_path.is_file():
        raise HTTPException(status_code=404)

    return {"reredisp": result}