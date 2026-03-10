# Example: Automated Git backup of the current project state
print("Starting automated backup...")
git.status()
git.commit("Automated backup from scripting console")
# git.push() # Uncomment to push to remote
print("Backup commit completed.")
