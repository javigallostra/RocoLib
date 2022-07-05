if "%~3"==""  (
    if "%~4"=="" (
        if "%~5"=="" (
            python .\scripts\py\add_gym.py -c %1 -n %2
        )
    ) else (
        python .\scripts\py\add_gym.py -c %1 -n %2 -l %4 %5
    )
) else ( 
    if "%~4"=="" (
        if "%~5"=="" (
            python .\scripts\py\add_gym.py -c %1 -n %2 -i %3
        )
    ) else ( 
        python .\scripts\py\add_gym.py -c %1 -n %2 -i %3 -l %4 %5
    )
)
