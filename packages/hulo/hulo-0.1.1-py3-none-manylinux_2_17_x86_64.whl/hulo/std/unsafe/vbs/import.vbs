Sub Import(path)
    Dim fso, file, code
    Set fso = CreateObject("Scripting.FileSystemObject")
    If Not fso.FileExists(path) Then
        WScript.Echo "Error: File not found - " & path
        WScript.Quit
    End If
    Set file = fso.OpenTextFile(path, 1)
    code = file.ReadAll
    file.Close
    ExecuteGlobal code
End Sub
