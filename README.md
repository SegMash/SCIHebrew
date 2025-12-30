Translate SCI game procedure:
Prerequisit:
Prepare gog game, and create src folder. Copy the sources from csi-scripts project. (find your game!) 
https://github.com/sluicebox/sci-scripts


1. fonts - I copied the fonts from other sci hebrew games and locate them in assets/kq4 directory.
2. Text.
    There are 2 kinds of strings. references and hard-coded
    The references are located in text file. In order to extract them run:
> python.exe .\scripts\extract_texts.py kq4_gog/src output_english.txt output_multi.txt output_format.txt
3. Use AI to translate. in case of string with multiple lines - put the multiple lines in new output file.
4. create mapping file:
You should run the script to map 3 kinds of messages: english, formatting, multiple lines.

> python scripts\map_files.py .\output_kq4\single_messages.txt .\output_kq4\single_messages_hebrew.txt .
\output_kq4\single_mapping.txt
> python scripts\map_files.py --multiline .\output_kq4\multi_messages.txt .\output_kq4\multi_messages_hebrew.txt .\output_kq4\single_mapping.txt --append
> python scripts\map_files.py .\output_kq4\format_messages.txt .\output_kq4\format_messages_hebrew.txt .\output_kq4\single_mapping.txt --append

5. extract strings hard-coded between {....}
> python.exe .\scripts\extract_strings.py --delimiter quotes kq4_gog/src output
6. USe AI again to translate the output
7. create mapping file for it
> python scripts\map_files.py .\output_kq4\hardcoded.txt .\output_kq4\hardcoded_hebrew.txt output_kq4\hardcoded_mapping.txt
7. Inject the strings into the src folder:
> replace_strings.py kq4_gog/src kq4_gog/src_heb output_kq4/hardcoded_mapping.txt
8. compare and override the scripts in original src folder.
9. Vocabulary
    export vocabulary:
> python.exe .\scripts\vocab_export.py kq4_gog output_kq4
10. Ui AI to add hebrew words.
11. run import and verify 2 things:
    No duplicates
    No words with space (more than one word)
> python.exe .\scripts\vocab_import.py output_kq4 kq4_work kq4_resources_copy
12. Fix scripts when you need to support better commands.
    Use SCICompanion - After fixing - compile again and extract resources.
13. Save all changed scripts(*.sc), compilied(script.*), text.* - in assets/<game> folder. - and check-in.
14. Check-in translated hebrew files.
15. check-in the vocabulary csv file.



1.  Clean all files from kq4_gog/src
2.  Restore resources from GOG orig game..
3. Restart SCICompanion
4. Copy files from sci-scripts to kq4_gog/src
5. Run .\scripts\replace_strings.py
6. Copy from src_heb to src
7. Compile all
8. extract scripts
9. copy all scripts to work dir.

For more manual changes
10. open each file with UltraEdit and compile from SCICompanion.
11. Compile all, Extract again and copy scripts to work dir.

Manual changes:
1. Main.sc (000) - some menu item names, remark lines
2. User.sc (996)- remark line
3. Interface.sc (255)- Fix place of dialog title
4. regUnicorn.sc (518) - Fix horn/unihorn
5. Room51.sc (051) - Fix lock/hole - keyhole
6. Room84.sc (084) - Fix box/pandora
7. Room69.sc (069) - Fix box/pandora
8. Room77.sc (077) - support swamp-egg
9. Room78.sc (078) - support swamp-egg




KQ5 - changes
1. Drop the subtitles files into work dir
2. 4.fon - from sq5?


Notes:
How to push into scumm
1. Run git remote make sure you have these
PS C:\Users\SEGEVMA\source\repos\scummvm> git remote -v
origin  https://github.com/SegMash/scummvm.git (fetch)
origin  https://github.com/SegMash/scummvm.git (push)
upstream        https://github.com/scummvm/scummvm.git (fetch)
upstream        https://github.com/scummvm/scummvm.git (push)

2. Remove proxy settings:
Remove-Item Env:\HTTP_PROXY -ErrorAction SilentlyContinue; Remove-Item Env:\HTTPS_PROXY -ErrorAction SilentlyContinue; Remove-Item Env:\http_proxy -ErrorAction SilentlyContinue; Remove-Item Env:\https_proxy -ErrorAction SilentlyContinue; git config --global --unset http.proxy; git config --global --unset https.proxy

3. Fetch latest changes from upstream
git fetch upstream

4. stash changes
git stash
5. Now update my master with upsteam!
git checkout master
git merge upstream/master
6. Push to origin (fork)
git push origin master
7. Restore my stash changes
git stash pop
8. Check status of diff
git diff --stat
9. Go to visual studio, stash and commit the changes with a proper message
10. git push origin master
11. Create the PR


git checkout -b adding_harpy_patch_v2
git reset --hard upstream/master
git cherry-pick b6c32625830
git log --oneline upstream/master..adding_harpy_patch_v2
-> Push to the fork
git push origin adding_harpy_patch_v2

To reset my workspace like the upstream:
git checkout master
git reset --hard upstream/master
git push origin master --force
git branch -D adding_harpy_patch_v2
git push origin --delete adding_harpy_patch_v2