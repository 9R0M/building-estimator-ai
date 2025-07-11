import styles from "../styles/App.module.css";

type NumberInputTypeMenuProps = {
  name: string;
  state: number;
  setState: React.Dispatch<React.SetStateAction<number>>;
};

export default function NumberInputTypeMenu(props: NumberInputTypeMenuProps) {
  const { name, state, setState } = props;
  return (
    <div className={styles.formGroup}>
      <label>{name}</label>
      <input
        type="number"
        value={state}
        onChange={(e) => setState(Number(e.target.value))}
      />
    </div>
  );
}
