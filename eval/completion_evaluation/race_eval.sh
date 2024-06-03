python eval_by_race.py $1 $2 && python single_token_viz_by_race.py $1 $2 && python tablize_by_race.py $1 $2 && python analyze_by_profession.py $1 $2
cd ..
python plot.py $1 $2