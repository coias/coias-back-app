import shutil
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile
from API.utils import pj_path, split_list, convertFits2PngCoords, convertPng2FitsCoords
import API.config as config
import os


router = APIRouter(
    tags=["files"],
    responses={404: {"description": "Not found"}},
)


@router.get("/unknown_disp", summary="unknown_disp.txtを配列で取得", tags=["files"])
def get_unknown_disp(pj: int = -1):
    disp_path = pj_path(pj) / "unknown_disp.txt"

    if not disp_path.is_file():
        raise HTTPException(status_code=404)

    with disp_path.open() as f:
        result = f.read()

    result = split_list(result.split(), 4)

    return {"result": result}


@router.get("/log", summary="log.txtを配列で取得", tags=["files"])
def get_log(pj: int = -1):
    log_path = pj_path(pj) / "log.txt"

    if not log_path.is_file():
        raise HTTPException(status_code=404)

    with log_path.open() as f:
        result = f.read()

    if result == "":
        raise HTTPException(status_code=404)

    return {"result": result.split("\n")}


@router.get("/karifugo_disp", summary="karifugo_disp.txtを配列で取得", tags=["files"])
def get_karifugo_disp(pj: int = -1):
    disp_path = pj_path(pj) / "karifugo_disp.txt"

    if not disp_path.is_file():
        raise HTTPException(status_code=404)

    with disp_path.open() as f:
        result = f.read()

    result = split_list(result.split(), 4)

    return {"result": result}


@router.get("/numbered_disp", summary="numbered_disp.txtを配列で取得", tags=["files"])
def get_numbered_disp(pj: int = -1):
    disp_path = pj_path(pj) / "numbered_disp.txt"

    if not disp_path.is_file():
        raise HTTPException(status_code=404)

    with disp_path.open() as f:
        result = f.read()

    result = split_list(result.split(), 4)

    return {"result": result}


@router.post("/uploadfiles", summary="fileアップロード", tags=["files"])
async def create_upload_files(
    files: list[UploadFile] = None, doUploadFiles: bool = False
):
    """
    複数のファイルをアップロードする場合はこちらのページを使用すると良い

    [localhost:8000](http://localhost:8000/)

    __参考__
    - [Request Files - FastAPI](https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile)
    - [フォーム - React](https://ja.reactjs.org/docs/forms.html)
    """  # noqa:E501

    dt = str(datetime.now())
    log = {
        "file_list": [],
        "create_time": [],
        "zip_upload": [],
    }
    log_path = config.FILES_PATH / "log"

    # logファイルがあれば読み込み
    if log_path.is_file():

        with log_path.open(mode="r") as conf:
            conf_json = conf.read()

        if not conf_json == "":
            log = json.loads(conf_json)

    # projectに割り振られる番号を生成
    if log["file_list"]:
        last_project = log["file_list"][-1] + 1
    else:
        last_project = 1

    # logを更新
    log["file_list"].append(last_project)
    log["create_time"].append(dt)
    log["zip_upload"].append(False)

    # logを書き込み
    json_str = json.dumps(log)
    with log_path.open(mode="w") as conf:
        conf.write(json_str)

    # プロジェクトディレクトリを作成
    file_name = str(log["file_list"][-1])
    current_project_folder_path = config.FILES_PATH / file_name
    current_project_folder_path.mkdir()

    # fileを保存
    if doUploadFiles:
        for file in files:
            tmp_path = current_project_folder_path / file.filename

            try:
                with tmp_path.open("wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

            finally:
                file.file.close()

    # プロジェクトディレクトリの内容を取得
    files_dir = [fd.name for fd in config.FILES_PATH.iterdir() if fd.is_dir()]
    project_files = [pf.name for pf in current_project_folder_path.iterdir()]

    files_dir.sort(key=int)
    project_files.sort()

    return {"tmp_files_projects": files_dir, "project_files": project_files, "log": log}


@router.delete("/deletefiles", summary="tmp_imageの中身を削除", tags=["files"], status_code=200)
def run_deletefiles():

    for f in config.IMAGES_PATH.glob("*.png"):
        if f.is_file:
            f.unlink()


@router.put("/copy", summary="プロジェクトから「tmp_image」へpng画像コピー", tags=["files"])
def run_copy(pj: int = -1):
    # fmt: off
    """
    「tmp_image」にあるpng画像はnginxによって配信されます。  
    配信されているpng画像のリストを配列で返却します。

    __res__

    ```JSON
    {
        "result": [
            "1_disp-coias.png",
            "1_disp-coias_nonmask.png",
            "2_disp-coias.png",
            "2_disp-coias_nonmask.png",
            "3_disp-coias.png",
            "3_disp-coias_nonmask.png",
            "4_disp-coias.png",
            "4_disp-coias_nonmask.png",
            "5_disp-coias.png",
            "5_disp-coias_nonmask.png",
        ]
    }
    ```
    """ # noqa
    # fmt: on
    for f in pj_path(pj).glob("*.png"):
        if f.is_file():
            shutil.copy(f, config.IMAGES_PATH)

    file_list = []
    for i in config.IMAGES_PATH.glob("*.png"):
        file_list.append(i.name)
    file_list.sort()

    return {"result": file_list}


@router.put("/memo", summary="outputを出力", tags=["files"])
def run_memo(output_list: list, pj: int = -1):
    # fmt: off
    """
    フロントから渡されたbodyの配列からmemo.txtを出力します。

    __body__

    ```JSON
    [
        "000001",
        "000010",
        "000013",
        "000012",
        "000005",
        "000003",
        "000004",
        "000009",
        "000000",
        "000006",
        "000014"
    ]
    ```
    """ # noqa
    # fmt: on

    memo = ""
    result = ""
    memo_path = pj_path(pj) / "memo.txt"

    for i, list in enumerate(output_list):
        memo = memo + str(list)
        if not i == (len(output_list) - 1):
            memo = memo + "\n"

    with memo_path.open(mode="w") as f:
        f.write(memo)

    with memo_path.open(mode="r") as f:
        result = f.read()

    return {"memo.txt": result}


@router.get("/memo", summary="memoを取得", tags=["files"])
def get_memo(pj: int = -1):
    # fmt: off
    """
    memo.txtの内容を取得してフロントに返却します。

    __body__

    ```JSON
    [
        "000001",
        "000010",
        "000013",
        "000012",
        "000005",
        "000003",
        "000004",
        "000009",
        "000000",
        "000006",
        "000014"
    ]
    ```
    """ # noqa
    # fmt: on

    memo_path = pj_path(pj) / "memo.txt"

    if not memo_path.is_file():
        raise HTTPException(status_code=404)

    with memo_path.open() as f:
        result = f.read()

    if result == "":
        raise HTTPException(status_code=404)

    return {"memo": result.split("\n")}


@router.get("/memo_manual", summary="memo_manualを取得", tags=["files"])
def get_memomanual(pj: int = -1):
    # fmt: off
    """
    memo_manual.txtの内容を取得してフロントに返却します。

    __body__

    ```JSON
    [
        "000001",
        "000010",
        "000013",
        "000012",
        "000005",
        "000003",
        "000004",
        "000009",
        "000000",
        "000006",
        "000014"
    ]
    ```
    """ # noqa
    # fmt: on

    memo_path = pj_path(pj) / "memo_manual.txt"

    if not memo_path.is_file():
        raise HTTPException(status_code=404)

    with memo_path.open() as f:
        readResult = f.read()

    if readResult == "":
        raise HTTPException(status_code=404)

    memo_manual = []
    for line in readResult.split("\n"):
        splitedLine = line.split(" ")
        result = (
            splitedLine[0]
            + " "
            + splitedLine[1]
            + " "
            + convertFits2PngCoords([int(splitedLine[2]), int(splitedLine[3])])
            + " "
            + convertFits2PngCoords([int(splitedLine[4]), int(splitedLine[5])])
            + " "
            + convertFits2PngCoords([int(splitedLine[6]), int(splitedLine[7])])
            + " "
            + convertFits2PngCoords([int(splitedLine[8]), int(splitedLine[9])])
        )
        memo_manual.append(result)

    return {"memo_manual": memo_manual}


@router.put(
    "/manual_name_modify_list",
    summary="manual_name_modify_list.txtを書き込み",
    tags=["files"],
)
def write_modify_list(modifiedList: list, pj: int = -1):
    # fmt: off
    """
    textの配列を、manual_name_modify_list.txtに書き込みます。
    """ # noqa
    # fmt: on


@router.put("/get_mpc", summary="2回目以降にレポートモードに入ったときにsend_mpcを取得するだけのAPI", tags=["files"])
def get_mpc(pj: int = -1):
    send_path = pj_path(pj) / "send_mpc.txt"
    result = ""

    with send_path.open(mode="r") as f:
        result = f.read()

    if not send_path.is_file():
        raise HTTPException(status_code=404)

    return {"send_mpc": result}


@router.get(
    "/final_disp", summary="最終確認モードで表示させる天体一覧を記したfinal_disp.txtを取得する", tags=["files"]
)
def get_finaldisp(pj: int = -1):
    final_disp_path = pj_path(pj) / "final_disp.txt"

    if not final_disp_path.is_file():
        raise HTTPException(status_code=404)

    with final_disp_path.open() as f:
        result = f.read()

    result = split_list(result.split(), 4)

    return {"result": result}


@router.get("/final_all", summary="final_allを取得", tags=["files"])
def get_finalall(pj: int = -1):

    final_all_path = pj_path(pj) / "final_all.txt"

    if not final_all_path.is_file():
        raise HTTPException(status_code=404)

    with final_all_path.open() as f:
        result = f.read()

    if result == "":
        raise HTTPException(status_code=404)

    return {"finalall": result}


@router.get(
    "/time_list",
    summary="画像の時刻リストが記載されたformatted_time_list.txtの内容を配列で取得",
    tags=["files"],
)
def get_time_list(pj: int = -1):
    time_list_path = pj_path(pj) / "formatted_time_list.txt"

    if not time_list_path.is_file():
        raise HTTPException(status_code=404)

    with time_list_path.open() as f:
        result = f.readlines()

    for i in range(len(result)):
        result[i] = result[i].rstrip("\n")

    return {"result": result}


@router.get(
    "/predicted_disp",
    summary="直近の測定データから予測された天体の位置を記載したpredicted_disp.txtを取得する",
    tags=["files"],
)
def get_predicted_disp(pj: int = -1):
    predicted_disp_path = pj_path(pj) / "predicted_disp.txt"

    if not predicted_disp_path.is_file():
        raise HTTPException(status_code=404)

    with predicted_disp_path.open() as f:
        result = f.read()

    result = split_list(result.split(), 5)

    return {"result": result}


@router.get(
    "/AstMPC_refreshed_time",
    summary="小惑星軌道データが最後にダウンロードされAstMPC.edbが更新された日時を取得する",
    tags=["files"],
)
def get_AstMPC_refreshed_time(pj: int = -1):
    AstMPC_path = config.COIAS_PARAM_PATH / "AstMPC.edb"

    if not AstMPC_path.is_file():
        result = "小惑星軌道データが存在しません.「小惑星データ更新」ボタンを押して下さい."
    else:
        modified_unix_time = os.path.getmtime(AstMPC_path)
        dt = datetime.fromtimestamp(modified_unix_time)
        result = dt.strftime("最終更新: %Y年%m月%d日%H時")

    return {"result": result}


@router.get("/manual_delete_list", summary="manual_delete_list.txtを取得", tags=["files"])
def get_manual_delete_list(pj: int = -1):
    # fmt: off
    """
    manual_delete_list.txtの内容を取得しフロントに返却します。

    __body__

    ```
    [
        ["H000005", "0"],
        ["H000005", "3"],
        ["H000012", "3"],
    ]
    ```
    """ # noqa
    # fmt: on

    manual_delete_path = pj_path(pj) / "manual_delete_list.txt"

    if not manual_delete_path.is_file():
        raise HTTPException(status_code=404)

    with manual_delete_path.open() as f:
        result = f.read()

    result = split_list(result.split(), 2)

    return {"result": result}


@router.put("/manual_delete_list", summary="manual_delete_list.txtの出力", tags=["files"])
def run_manual_delete_list(output_list: list, pj: int = -1):
    # fmt: off
    """
    フロントから受け取ったbodyの配列からmanual_delete_list.txtを出力します。

    __body__

    ```
    [
        "H000005 0",
        "H000005 3",
        "H000012 3",
    ]
    ```
    """ # noqa
    # fmt: on
    result = ""
    manual_delete_path = pj_path(pj) / "manual_delete_list.txt"

    with manual_delete_path.open(mode="w") as f:
        for line in output_list:
            f.write(line + "\n")

    with manual_delete_path.open(mode="r") as f:
        result = f.read()

    return {"manual_delete_list.txt": result}


@router.put("/memo_manual", summary="手動測定の出力", tags=["files"])
def run_memo_manual(output_list: list, pj: int = -1):
    # fmt: off
    """
    フロントから受け取ったbodyの配列からmemo_manual.txtを出力します。

    __body__

    ```JSON
    [
        "000001",
        "000010",
        "000013",
        "000012",
        "000005",
        "000003",
        "000004",
        "000009",
        "000000",
        "000006",
        "000014"
    ]
    ```
    """ # noqa
    # fmt: on

    memo_manual = ""
    result = ""
    memo_manual_path = pj_path(pj) / "memo_manual.txt"

    for list in output_list:
        for list_obj in list:
            translated_line = (
                str(list_obj["name"])
                + " "
                + str(list_obj["page"])
                + " "
                + convertPng2FitsCoords(
                    [int(list_obj["center"]["x"]), int(list_obj["center"]["y"])]
                )
                + " "
                + convertPng2FitsCoords(
                    [int(list_obj["actualA"]["x"]), int(list_obj["actualA"]["y"])]
                )
                + " "
                + convertPng2FitsCoords(
                    [int(list_obj["actualB"]["x"]), int(list_obj["actualB"]["y"])]
                )
                + " "
                + convertPng2FitsCoords(
                    [int(list_obj["actualC"]["x"]), int(list_obj["actualC"]["y"])]
                )
            )
            memo_manual = memo_manual + str(translated_line)
            if not (
                list_obj["name"] == output_list[-1][-1]["name"]
                and list_obj["page"] == output_list[-1][-1]["page"]
            ):
                memo_manual = memo_manual + "\n"

    with memo_manual_path.open(mode="w") as f:
        f.write(memo_manual)

    with memo_manual_path.open(mode="r") as f:
        result = f.read()

    return {"memo_manual.txt": result}


@router.put("/redisp", summary="再描画による確認作業", tags=["files"])
def run_redisp(pj: int = -1):
    """
    redisp.txtの内容をを配列で取得しフロントに返却

    __res__

    ```JSON
    {
        "result": [
            [
                "w7794",
                "3",
                "1965.52",
                "424.56"
            ],
            [
                "w7794",
                "2",
                "1927.21",
                "416.32"
            ]
        ]
    }
    ```

    """  # noqa

    redisp_path = pj_path(pj) / "redisp.txt"

    if not redisp_path.is_file():
        raise HTTPException(status_code=404)

    with redisp_path.open() as f:
        result = f.read()

    result = split_list(result.split(), 4)

    return {"result": result}